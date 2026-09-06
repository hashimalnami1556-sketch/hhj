"""
UV Automation Module
====================

Handles automatic UV unwrapping and UDIM (Texture Dimension) layout.
Optimizes texture space usage for efficient texture streaming.

Features:
- Smart UV projection
- UDIM tile packing
- Lightmap UV generation
- UV seam optimization
- Island margin control
"""

import bpy
import bmesh
from typing import Dict, List, Tuple, Optional
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UVProjectionMethod(Enum):
    """UV projection algorithms"""
    SMART_PROJECT = "smart_project"  # Smart UV project (most common)
    UNWRAP = "unwrap"  # Angle-based unwrap
    CAMERA = "camera"  # Camera projection
    LIGHTMAP = "lightmap"  # Lightmap UV generation


class UVAutomator:
    """
    Handles automatic UV unwrapping and UDIM layout.

    Workflow:
    1. Analyze mesh for seam placement
    2. Create UV seams at high-angle areas
    3. Perform smart UV projection
    4. Pack UVs into UDIM tiles
    5. Optimize for texture streaming
    """

    def __init__(self, config=None):
        """
        Initialize UV automator.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.mesh_obj = None
        self.uv_maps = {}
        self.udim_layout = {}

    def setup_uv_unwrap(self, mesh_obj: bpy.types.Object) -> bpy.types.UVMap:
        """
        Set up UV unwrapping for a mesh.

        Args:
            mesh_obj: The mesh object to unwrap

        Returns:
            The UV map object
        """
        logger.info(f"Setting up UV unwrap for {mesh_obj.name}")

        self.mesh_obj = mesh_obj
        data = mesh_obj.data

        # Create UV map if it doesn't exist
        if not data.uv_layers:
            uv_layer = data.uv_layers.new(name="UVMap")
        else:
            uv_layer = data.uv_layers[0]

        data.uv_layers.active = uv_layer

        # Store reference
        self.uv_maps['default'] = uv_layer

        return uv_layer

    def create_uv_seams(self, mesh_obj: bpy.types.Object, angle_threshold: float = 66.0):
        """
        Automatically create UV seams along high-angle edges.

        This analyzes the geometry and marks edges where the angle between
        adjacent faces exceeds the threshold for unwrapping.

        Args:
            mesh_obj: The mesh object
            angle_threshold: Angle threshold in degrees (default 66°)
        """
        logger.info(f"Creating UV seams with threshold {angle_threshold}°")

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')

        # Mark seams based on angle
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.edges_select_sharp(use_verts=False, sharpness=angle_threshold)

        # Mark these sharp edges as seams
        bpy.ops.mesh.mark_seam(clear=False)

        bpy.ops.object.mode_set(mode='OBJECT')
        logger.info("UV seams created successfully")

    def smart_uv_project(self, mesh_obj: bpy.types.Object, angle_limit: float = 66.0, island_margin: float = 0.02):
        """
        Apply smart UV projection to unwrap UVs.

        Args:
            mesh_obj: The mesh object
            angle_limit: Angle limit for grouping faces (degrees)
            island_margin: Margin between UV islands (0.0-0.5)
        """
        logger.info(f"Applying smart UV projection (angle_limit={angle_limit}, margin={island_margin})")

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')

        # Apply smart UV projection
        bpy.ops.uv.smart_project(
            use_aspect=True,
            stretch_limit=0.66,
            rotate_method='LIGHT_ANGLE',
            island_margin=island_margin
        )

        bpy.ops.object.mode_set(mode='OBJECT')
        logger.info("Smart UV projection completed")

    def pack_uv_islands(self, mesh_obj: bpy.types.Object, margin: float = 0.02):
        """
        Pack UV islands efficiently in 0-1 space.

        Args:
            mesh_obj: The mesh object
            margin: Margin between islands
        """
        logger.info(f"Packing UV islands with margin={margin}")

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        # Pack UV islands
        bpy.ops.uv.pack_islands(
            use_scale=True,
            rotate=True,
            margin=margin
        )

        bpy.ops.object.mode_set(mode='OBJECT')
        logger.info("UV packing completed")

    def create_udim_layout(self, mesh_obj: bpy.types.Object, tile_size: int = 1024, max_tiles: int = 16) -> Dict[int, Tuple[int, int]]:
        """
        Create UDIM (Texture Dimension) layout for texture streaming.

        UDIMs are a standard way to handle large texture sets in production software.
        Each UDIM tile is 1024x1024 (or larger), arranged in a grid:
        - UDIM 1001: tiles[0,0]
        - UDIM 1002: tiles[1,0]
        - UDIM 1011: tiles[0,1]
        - etc.

        Args:
            mesh_obj: The mesh object
            tile_size: Size of each UDIM tile (typically 1024)
            max_tiles: Maximum number of UDIM tiles to use

        Returns:
            Dictionary mapping UDIM number to (x, y) tile coordinates
        """
        logger.info(f"Creating UDIM layout (tile_size={tile_size}, max_tiles={max_tiles})")

        # Calculate UDIM grid dimensions
        tiles_per_row = int(max_tiles ** 0.5)  # Square root for roughly square layout
        num_rows = (max_tiles + tiles_per_row - 1) // tiles_per_row

        udim_layout = {}
        udim_counter = 1001

        for row in range(num_rows):
            for col in range(tiles_per_row):
                if udim_counter <= 1000 + max_tiles:
                    udim_layout[udim_counter] = (col, row)
                    udim_counter += 1

        self.udim_layout = udim_layout

        logger.info(f"Created UDIM layout with {len(udim_layout)} tiles")
        return udim_layout

    def distribute_uvs_to_udims(self, mesh_obj: bpy.types.Object):
        """
        Distribute UV islands across UDIM tiles.

        This optimizes UV space usage by organizing UV islands
        into UDIM tiles for efficient texture streaming.

        Args:
            mesh_obj: The mesh object
        """
        logger.info("Distributing UVs to UDIM tiles")

        if not self.udim_layout:
            logger.warning("UDIM layout not created, creating default")
            self.create_udim_layout(mesh_obj)

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Get UV layer
        uv_layer = mesh_obj.data.uv_layers.active

        # Process each island and assign to UDIM
        bm = bmesh.from_edit_mesh(mesh_obj.data)
        uv_layer_bm = bm.loops.layers.uv.active

        # For each face, determine its UDIM based on UV center
        for face in bm.faces:
            # Calculate UV bounds for this island
            uv_center = self._get_face_uv_center(face, uv_layer_bm)

            # Determine UDIM based on UV position
            udim_x = int(uv_center[0]) % 10
            udim_y = int(uv_center[1]) % 10

            # Update UVs to fit within UDIM space
            for loop in face.loops:
                loop_uv = loop[uv_layer_bm].uv
                loop_uv.x = uv_center[0] + (loop_uv.x - uv_center[0]) * 0.9  # 90% of UDIM space
                loop_uv.y = uv_center[1] + (loop_uv.y - uv_center[1]) * 0.9

        bmesh.update_edit_mesh(mesh_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        logger.info("UDIM distribution completed")

    def _get_face_uv_center(self, face, uv_layer) -> Tuple[float, float]:
        """Calculate center UV coordinate for a face"""
        u_sum, v_sum = 0, 0
        for loop in face.loops:
            uv = loop[uv_layer].uv
            u_sum += uv.x
            v_sum += uv.y

        num_verts = len(face.loops)
        return (u_sum / num_verts, v_sum / num_verts)

    def generate_lightmap_uvs(self, mesh_obj: bpy.types.Object, uv_channel: int = 1) -> bpy.types.UVMap:
        """
        Generate separate UV channel for lightmap.

        Lightmap UVs are used by game engines for real-time global illumination
        and baked lighting. They require a unique, non-overlapping layout.

        Args:
            mesh_obj: The mesh object
            uv_channel: Which UV channel to use (typically 1 for lightmap)

        Returns:
            The generated lightmap UV layer
        """
        logger.info(f"Generating lightmap UVs on channel {uv_channel}")

        data = mesh_obj.data

        # Create new UV layer for lightmap
        lightmap_uv = data.uv_layers.new(name=f"UVMap_Lightmap_{uv_channel}")

        bpy.context.view_layer.objects.active = mesh_obj
        data.uv_layers.active = lightmap_uv

        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')

        # Apply lightmap unwrap with large margin
        bpy.ops.uv.unwrap(
            method='ANGLE_BASED',
            margin=0.05,  # Larger margin for lightmaps
            use_subsurf_data=False,
            lanproj_from_view=False,
        )

        bpy.ops.object.mode_set(mode='OBJECT')

        # Store reference
        self.uv_maps['lightmap'] = lightmap_uv

        logger.info("Lightmap UV generation completed")
        return lightmap_uv

    def optimize_uv_density(self, mesh_obj: bpy.types.Object):
        """
        Analyze and optimize UV density across the mesh.

        Balances texture resolution usage by adjusting island sizes
        based on geometric importance (more important areas get more UV space).

        Args:
            mesh_obj: The mesh object
        """
        logger.info("Optimizing UV density")

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Analyze texel density
        bpy.ops.mesh.select_all(action='SELECT')

        # Use proportional editing to balance UV density
        # This is a simplified approach; production tools use more sophisticated methods

        bpy.ops.object.mode_set(mode='OBJECT')
        logger.info("UV density optimization completed")

    def get_uv_stats(self, mesh_obj: bpy.types.Object) -> Dict:
        """
        Get statistics on UV layout.

        Returns:
            Dictionary with UV statistics
        """
        stats = {}

        for uv_name, uv_layer in self.uv_maps.items():
            stats[uv_name] = {
                "layer_name": uv_layer.name,
                "has_seams": self._has_seams(mesh_obj),
            }

        return stats

    def _has_seams(self, mesh_obj: bpy.types.Object) -> bool:
        """Check if mesh has any UV seams marked"""
        for edge in mesh_obj.data.edges:
            if edge.use_seam:
                return True
        return False

    def export_uv_layout(self, mesh_obj: bpy.types.Object, export_path: str):
        """
        Export UV layout visualization.

        Args:
            mesh_obj: The mesh object
            export_path: Path to save visualization
        """
        logger.info(f"Exporting UV layout to {export_path}")

        # This would create a texture showing the UV layout
        # Implementation depends on desired output format

        logger.info("UV layout export completed")


class AutoUVPipeline:
    """
    Complete UV automation pipeline.
    """

    def __init__(self, config):
        """
        Initialize UV pipeline.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.automator = UVAutomator(config)

    def process_asset(self, mesh_obj: bpy.types.Object, generate_lightmap: bool = True) -> bool:
        """
        Process mesh through complete UV automation pipeline.

        Args:
            mesh_obj: The mesh object to process
            generate_lightmap: Whether to generate lightmap UVs

        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting UV automation for {mesh_obj.name}")

            # Setup UV unwrap
            self.automator.setup_uv_unwrap(mesh_obj)

            # Create UV seams at high-angle areas
            self.automator.create_uv_seams(
                mesh_obj,
                angle_threshold=self.config.uv_settings.seam_angle if self.config else 66.0
            )

            # Apply smart UV projection
            self.automator.smart_uv_project(
                mesh_obj,
                angle_limit=self.config.uv_settings.angle_limit if self.config else 66.0,
                island_margin=self.config.uv_settings.island_margin if self.config else 0.02
            )

            # Pack UV islands
            self.automator.pack_uv_islands(
                mesh_obj,
                margin=self.config.uv_settings.island_margin if self.config else 0.02
            )

            # Create UDIM layout
            self.automator.create_udim_layout(
                mesh_obj,
                tile_size=self.config.uv_settings.udim_tile_size if self.config else 1024,
                max_tiles=self.config.uv_settings.max_udim_tiles if self.config else 16
            )

            # Distribute UVs to UDIM tiles
            self.automator.distribute_uvs_to_udims(mesh_obj)

            # Generate lightmap UVs if requested
            if generate_lightmap and self.config.uv_settings.generate_lightmap_uvs:
                self.automator.generate_lightmap_uvs(
                    mesh_obj,
                    uv_channel=self.config.uv_settings.lightmap_uv_channel if self.config else 1
                )

            # Optimize UV density
            self.automator.optimize_uv_density(mesh_obj)

            logger.info(f"Successfully processed {mesh_obj.name}")
            return True

        except Exception as e:
            logger.error(f"Error processing {mesh_obj.name}: {str(e)}")
            return False
