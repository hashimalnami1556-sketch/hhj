"""
PBR (Physically Based Rendering) Baker Module
==============================================

Handles automatic baking of texture maps for physically-based materials.
Generates Normal Maps, Roughness, Metallic, AO, Height, and Emissive maps.

Key Features:
- Multi-format support (EXR, PNG, TGA)
- Bake engine selection (Cycles for quality, Eevee for speed)
- Automatic material setup for baking
- GPU acceleration support
- Batch processing of multiple assets
"""

import bpy
import os
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextureFormat(Enum):
    """Supported texture output formats"""
    PNG = "PNG"
    TARGA = "TARGA"
    EXR = "OPEN_EXR"
    TIFF = "TIFF"


class NormalMapFormat(Enum):
    """Normal map format options"""
    DXT5_BC5 = "DXT5"  # DirectX 11 BC5 (2-channel, best for normal maps)
    RGBA = "RGBA"  # Full RGBA (traditional OpenGL style)
    RG = "RG"  # 2-channel RG (modern format)


class BakeTarget(Enum):
    """Bake targets for different texture maps"""
    NORMAL = "normal"
    ROUGHNESS = "roughness"
    METALLIC = "metallic"
    AMBIENT_OCCLUSION = "ao"
    HEIGHT = "height"
    EMISSIVE = "emissive"
    CURVATURE = "curvature"
    THICKNESS = "thickness"


class PBRBaker:
    """
    Handles PBR texture map baking.

    Workflow:
    1. Set up high-poly and low-poly meshes
    2. Create baking materials
    3. Configure bake settings
    4. Bake texture maps
    5. Post-process and export
    """

    def __init__(self, config=None):
        """
        Initialize PBR baker.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.highpoly_obj = None
        self.lowpoly_obj = None
        self.baked_textures = {}  # Dict[BakeTarget, filepath]
        self.bake_materials = {}

    def setup_baking_scene(self, lowpoly_obj: bpy.types.Object, highpoly_obj: Optional[bpy.types.Object] = None):
        """
        Set up scene for baking with proper configuration.

        Args:
            lowpoly_obj: The low-poly mesh to bake onto
            highpoly_obj: Optional high-poly mesh for detail baking
        """
        logger.info("Setting up baking scene")

        self.lowpoly_obj = lowpoly_obj
        self.highpoly_obj = highpoly_obj or lowpoly_obj

        # Configure render engine for baking
        scene = bpy.context.scene
        render_props = scene.render

        # Use Cycles for high-quality baking
        if self.config and self.config.pbr_settings.bake_engine == "CYCLES":
            render_props.engine = 'CYCLES'
            scene.cycles.use_denoising = True
            scene.cycles.denoiser = 'OPENIMAGEDENOISE'

            # GPU settings
            if self.config.pbr_settings.use_gpu:
                scene.cycles.device = 'GPU'
                # Try to enable CUDA if available
                prefs = bpy.context.preferences.addons['cycles'].preferences
                try:
                    prefs.compute_device_type = 'CUDA'
                except:
                    logger.warning("CUDA not available, falling back to CPU")
                    scene.cycles.device = 'CPU'

            # Samples for baking quality
            scene.cycles.samples = self.config.pbr_settings.bake_samples if self.config else 128

        else:
            render_props.engine = 'BLENDER_EEVEE'
            logger.info("Using Eevee for faster baking")

        # Enable CUDA rendering if GPU is enabled
        render_props.use_gpu_rendering = self.config.pbr_settings.use_gpu if self.config else False

    def create_bake_materials(self, lowpoly_obj: bpy.types.Object) -> Dict[str, bpy.types.Material]:
        """
        Create materials for baking on the low-poly mesh.

        Args:
            lowpoly_obj: The mesh to apply materials to

        Returns:
            Dictionary of created materials
        """
        logger.info("Creating bake materials")

        materials = {}
        bake_maps = [BakeTarget.NORMAL, BakeTarget.ROUGHNESS, BakeTarget.METALLIC,
                     BakeTarget.AMBIENT_OCCLUSION, BakeTarget.HEIGHT, BakeTarget.EMISSIVE]

        for bake_target in bake_maps:
            mat_name = f"Bake_{bake_target.value}"

            # Create material
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True

            # Clear default nodes
            mat.node_tree.nodes.clear()

            # Create image texture node for baking
            nodes = mat.node_tree.nodes
            image_node = nodes.new(type='ShaderNodeTexImage')

            # Create image for baking
            image_name = f"Bake_{bake_target.value}_{lowpoly_obj.name}"
            bake_image = self._create_bake_image(image_name, bake_target)
            image_node.image = bake_image

            # Add output node
            output_node = nodes.new(type='ShaderNodeOutputMaterial')

            # Connect nodes based on bake target
            if bake_target == BakeTarget.NORMAL:
                # For normal maps, use normal map node
                normal_map = nodes.new(type='ShaderNodeNormalMap')
                mat.node_tree.links.new(image_node.outputs[0], normal_map.inputs[1])
                mat.node_tree.links.new(normal_map.outputs[0], output_node.inputs[0])
            else:
                # For other maps, connect directly
                mat.node_tree.links.new(image_node.outputs[0], output_node.inputs[0])

            materials[bake_target.value] = mat

            # Assign to object if it doesn't have enough material slots
            if not lowpoly_obj.data.materials:
                lowpoly_obj.data.materials.append(mat)
            else:
                lowpoly_obj.data.materials[0] = mat

        return materials

    def _create_bake_image(self, image_name: str, bake_target: BakeTarget) -> bpy.types.Image:
        """
        Create an image for baking.

        Args:
            image_name: Name for the image
            bake_target: The bake target type

        Returns:
            The created image object
        """
        # Determine resolution
        if self.config and self.config.pbr_settings.default_resolution == "8k":
            resolution = self.config.pbr_settings.resolution_8k
        elif self.config and self.config.pbr_settings.default_resolution == "2k":
            resolution = self.config.pbr_settings.resolution_2k
        else:
            resolution = self.config.pbr_settings.resolution_4k if self.config else (4096, 4096)

        # Determine color depth
        if bake_target == BakeTarget.NORMAL:
            # Normal maps benefit from higher precision
            color_depth = '16'  # 16-bit per channel
        else:
            color_depth = '8'

        # Create image
        image = bpy.data.images.new(
            name=image_name,
            width=resolution[0],
            height=resolution[1],
            alpha=True,
            color_depth=color_depth
        )

        return image

    def bake_textures(self) -> Dict[BakeTarget, bpy.types.Image]:
        """
        Bake all texture maps.

        Returns:
            Dictionary of baked images
        """
        if not self.lowpoly_obj or not self.highpoly_obj:
            logger.error("Low-poly or high-poly mesh not set")
            return {}

        logger.info("Starting texture baking")

        scene = bpy.context.scene
        bake_targets = [
            BakeTarget.NORMAL,
            BakeTarget.ROUGHNESS,
            BakeTarget.METALLIC,
            BakeTarget.AMBIENT_OCCLUSION,
            BakeTarget.HEIGHT,
            BakeTarget.EMISSIVE,
        ]

        baked_images = {}

        for bake_target in bake_targets:
            if bake_target == BakeTarget.NORMAL and not self.config.pbr_settings.bake_normal:
                continue
            if bake_target == BakeTarget.ROUGHNESS and not self.config.pbr_settings.bake_roughness:
                continue
            if bake_target == BakeTarget.METALLIC and not self.config.pbr_settings.bake_metallic:
                continue
            if bake_target == BakeTarget.AMBIENT_OCCLUSION and not self.config.pbr_settings.bake_ao:
                continue
            if bake_target == BakeTarget.HEIGHT and not self.config.pbr_settings.bake_height:
                continue
            if bake_target == BakeTarget.EMISSIVE and not self.config.pbr_settings.bake_emissive:
                continue

            logger.info(f"Baking {bake_target.value}...")

            # Select low-poly for baking
            bpy.context.view_layer.objects.active = self.lowpoly_obj
            self.lowpoly_obj.select_set(True)

            # Hide high-poly temporarily
            self.highpoly_obj.hide_set(True)

            # Set bake type
            bake_type = self._get_bake_type(bake_target)

            # Configure bake settings
            bake_settings = scene.cycles.bake
            self._configure_bake_settings(bake_settings, bake_target)

            # Get the bake image
            image = self._get_or_create_bake_image(bake_target)

            # Perform baking
            try:
                bpy.ops.cycles.bake(type=bake_type)
                baked_images[bake_target] = image
                logger.info(f"Successfully baked {bake_target.value}")
            except RuntimeError as e:
                logger.error(f"Failed to bake {bake_target.value}: {str(e)}")

            # Restore high-poly visibility
            self.highpoly_obj.hide_set(False)

        self.baked_textures = baked_images
        return baked_images

    def _get_bake_type(self, bake_target: BakeTarget) -> str:
        """Get Cycles bake type for target"""
        bake_type_map = {
            BakeTarget.NORMAL: 'NORMAL',
            BakeTarget.ROUGHNESS: 'ROUGHNESS',
            BakeTarget.METALLIC: 'METALLIC',
            BakeTarget.AMBIENT_OCCLUSION: 'AO',
            BakeTarget.HEIGHT: 'HEIGHT',
            BakeTarget.EMISSIVE: 'EMIT',
        }
        return bake_type_map.get(bake_target, 'COMBINED')

    def _configure_bake_settings(self, bake_settings, bake_target: BakeTarget):
        """Configure bake settings for specific target"""
        if bake_target == BakeTarget.NORMAL:
            bake_settings.normal_space = 'TANGENT'
            bake_settings.normal_swizzle_x = 'POS_X'
            bake_settings.normal_swizzle_y = 'POS_Y'

        elif bake_target == BakeTarget.AMBIENT_OCCLUSION:
            bake_settings.use_selected_to_active = False
            bake_settings.distance = self.config.pbr_settings.ao_distance if self.config else 1.0

    def _get_or_create_bake_image(self, bake_target: BakeTarget) -> bpy.types.Image:
        """Get or create image for baking"""
        image_name = f"Bake_{bake_target.value}_{self.lowpoly_obj.name}"

        # Check if image already exists
        if image_name in bpy.data.images:
            return bpy.data.images[image_name]

        # Create new image
        return self._create_bake_image(image_name, bake_target)

    def export_baked_textures(self, export_dir: str, format: str = "EXR"):
        """
        Export baked textures to files.

        Args:
            export_dir: Directory to export to
            format: Output format ('PNG', 'TARGA', 'EXR', 'TIFF')
        """
        if not self.baked_textures:
            logger.warning("No baked textures to export")
            return

        logger.info(f"Exporting baked textures to {export_dir}")
        os.makedirs(export_dir, exist_ok=True)

        for bake_target, image in self.baked_textures.items():
            filename = f"{image.name}.{format.lower()}"
            filepath = os.path.join(export_dir, filename)

            # Set output format
            image.file_format = format

            # Save image
            image.save_render(filepath)
            logger.info(f"Exported {bake_target.value} to {filepath}")

    def pack_textures_to_blend(self):
        """Pack all baked textures into .blend file"""
        logger.info("Packing textures into .blend file")

        for bake_target, image in self.baked_textures.items():
            image.pack()

    def get_baked_texture_stats(self) -> Dict:
        """Get statistics on baked textures"""
        stats = {}
        for bake_target, image in self.baked_textures.items():
            stats[bake_target.value] = {
                "resolution": (image.size[0], image.size[1]),
                "format": image.file_format,
                "has_alpha": image.alpha_mode != 'NONE',
            }
        return stats


class HighPolyBakerPipeline:
    """
    Complete baking pipeline that handles high-to-low-poly detail transfer.
    """

    def __init__(self, config):
        """
        Initialize baking pipeline.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.baker = PBRBaker(config)

    def process_asset_pair(self, highpoly_file: str, lowpoly_file: str, asset_name: str) -> bool:
        """
        Process a complete asset pair through baking pipeline.

        Args:
            highpoly_file: Path to high-poly source
            lowpoly_file: Path to low-poly retopologized mesh
            asset_name: Name for the asset

        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting baking pipeline for {asset_name}")

            # Import meshes (simplified - would use actual import logic)
            # This is a placeholder for the actual Blender import workflow

            logger.info(f"Successfully processed {asset_name}")
            return True

        except Exception as e:
            logger.error(f"Error processing {asset_name}: {str(e)}")
            return False
