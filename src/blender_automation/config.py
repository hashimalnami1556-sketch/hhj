"""
Configuration module for Blender asset automation pipeline.
Defines quality presets, LOD strategies, texture formats, and output directories.
"""

import os
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

class QualityPreset(Enum):
    """Asset quality and detail level presets"""
    MOBILE = "mobile"  # For mobile/VR, polygon limit: 50k
    CONSOLE = "console"  # For console, polygon limit: 150k
    PC_HIGH = "pc_high"  # For high-end PC, polygon limit: 500k
    PC_ULTRA = "pc_ultra"  # For ultra-high PC, polygon limit: 2M
    CINEMATIC = "cinematic"  # For cinematics, polygon limit: unlimited


class AssetCategory(Enum):
    """Asset type categories for specific workflows"""
    CHARACTER = "character"
    ENVIRONMENT = "environment"
    PROP = "prop"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    ARCHITECTURAL = "architectural"


@dataclass
class LODSettings:
    """Settings for Level of Detail generation"""
    # LOD levels (0=highest quality, 3=lowest)
    lod_levels: int = 4

    # Screen size thresholds (in pixels) for each LOD
    # LOD0: > 450px, LOD1: 200-450px, LOD2: 100-200px, LOD3: < 100px
    screen_thresholds: Tuple[float, float, float, float] = (450, 200, 100, 0)

    # Polygon reduction ratios per LOD
    # LOD0: 100%, LOD1: 50%, LOD2: 25%, LOD3: 10%
    reduction_ratios: Tuple[float, float, float, float] = (1.0, 0.5, 0.25, 0.1)

    # Decimate method: 'UNSUBDIV' (Un-subdivide), 'COLLAPSE' (Collapse)
    decimate_method: str = "COLLAPSE"

    # Preserve boundary edges and seams
    preserve_topology: bool = True

    # Smooth normals on reduced meshes
    smooth_normals: bool = True


@dataclass
class PBRBakingSettings:
    """Settings for Physically Based Rendering texture baking"""
    # Bake resolution options
    resolution_2k: Tuple[int, int] = (2048, 2048)
    resolution_4k: Tuple[int, int] = (4096, 4096)
    resolution_8k: Tuple[int, int] = (8192, 8192)
    default_resolution: str = "4k"  # "2k", "4k", or "8k"

    # Texture maps to bake
    bake_normal: bool = True
    bake_roughness: bool = True
    bake_metallic: bool = True
    bake_ao: bool = True  # Ambient Occlusion
    bake_curvature: bool = True
    bake_height: bool = True
    bake_emissive: bool = True

    # Normal map settings
    normal_format: str = "DXT5"  # "DXT5" (BC5 on DX11) or "EXR"
    normal_strength: float = 1.0

    # AO settings
    ao_distance: float = 1.0
    ao_samples: int = 256

    # Bake engine: 'CYCLES' for quality, 'EEVEE' for speed
    bake_engine: str = "CYCLES"

    # Cycles samples for baking (higher = better quality, slower)
    bake_samples: int = 128

    # Use GPU acceleration if available
    use_gpu: bool = True


@dataclass
class UVAutomationSettings:
    """Settings for UV unwrapping and UDIM layout"""
    # UDIM tile resolution (typically 1K, 2K, 4K)
    udim_tile_size: int = 1024

    # Number of UDIM tiles per asset (usually 4-16)
    max_udim_tiles: int = 16

    # Use smart UV project for unwrapping
    use_smart_uv: bool = True

    # UV seam angle threshold (degrees)
    seam_angle: float = 66.0

    # Island margin (padding between UV islands)
    island_margin: float = 0.02

    # Angle limit for packing
    angle_limit: float = 66.0

    # Stretch limit for packing
    stretch_limit: float = 0.1

    # Enable lightmap UV set generation (for static meshes)
    generate_lightmap_uvs: bool = True

    # Lightmap UV channel (usually channel 1 or 2)
    lightmap_uv_channel: int = 1

    # Unique UV sets per LOD
    uv_per_lod: bool = True


@dataclass
class RetopologySettings:
    """Settings for automatic retopology"""
    # Target polygon count for retopologized mesh
    target_poly_count: int = 50000  # For environment
    character_target_poly_count: int = 100000

    # Quadriflow voxel size (lower = higher detail)
    voxel_size: float = 0.1

    # Face count target (alternative to voxel size)
    use_face_count: bool = False
    face_count_target: int = 50000

    # Threshold for voxel grid resolution
    use_mesh_symmetry: bool = True

    # Preserve seams from UV islands
    preserve_uv_seams: bool = True


@dataclass
class TextureStreamingSettings:
    """Settings for virtual texture streaming"""
    # Virtual texture page size (typical: 128x128, 256x256)
    page_size: int = 128

    # Maximum virtual texture size
    max_vt_size: Tuple[int, int] = (16384, 16384)

    # Use 32-bit floating point for precision
    use_32bit: bool = False

    # Compression: "NONE", "DXT1", "DXT5", "BC4", "BC6"
    compression: str = "DXT5"


@dataclass
class BatchProcessingSettings:
    """Settings for batch processing workflows"""
    # Parallel processing threads
    num_threads: int = 4

    # Batch size (number of assets per batch)
    batch_size: int = 5

    # Enable GPU rendering
    use_gpu_rendering: bool = True

    # Output formats: "FBX", "GLTF", "USD", "UASSET"
    output_formats: List[str] = None  # Default to all

    # Clean up source files after export
    cleanup_temp_files: bool = True

    # Generate report after processing
    generate_report: bool = True


class BlenderAssetPipelineConfig:
    """Main configuration class for the entire asset pipeline"""

    def __init__(self, project_root: str = None):
        """
        Initialize pipeline configuration.

        Args:
            project_root: Root directory of the project (if None, uses current directory)
        """
        self.project_root = Path(project_root or os.getcwd())

        # Directory structure
        self.assets_dir = self.project_root / "assets"
        self.blender_dir = self.assets_dir / "blender"
        self.source_dir = self.blender_dir / "source"  # High-poly master files
        self.work_dir = self.blender_dir / "work"  # Working directory
        self.export_dir = self.blender_dir / "export"  # Final exports
        self.textures_dir = self.blender_dir / "textures"
        self.lod_dir = self.export_dir / "lods"
        self.pbr_dir = self.textures_dir / "pbr"
        self.cache_dir = self.work_dir / ".cache"

        # Create directories if they don't exist
        self._create_directories()

        # Load quality presets based on target platform
        self.quality_preset = QualityPreset.PC_HIGH

        # Settings instances
        self.lod_settings = LODSettings()
        self.pbr_settings = PBRBakingSettings()
        self.uv_settings = UVAutomationSettings()
        self.retopology_settings = RetopologySettings()
        self.texture_streaming = TextureStreamingSettings()
        self.batch_settings = BatchProcessingSettings()

        # Material library
        self.material_library = {
            "pbr_metallic": "PBR_Metallic",
            "pbr_specular": "PBR_Specular",
            "pbr_cloth": "PBR_Cloth",
            "pbr_skin": "PBR_Skin",
            "pbr_organic": "PBR_Organic",
        }

    def _create_directories(self):
        """Create all required directories"""
        for directory in [
            self.assets_dir,
            self.blender_dir,
            self.source_dir,
            self.work_dir,
            self.export_dir,
            self.textures_dir,
            self.lod_dir,
            self.pbr_dir,
            self.cache_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_quality_settings(self, category: AssetCategory) -> Dict:
        """
        Get appropriate quality settings for asset category.

        Args:
            category: The asset category (character, environment, etc.)

        Returns:
            Dictionary of quality settings
        """
        if category == AssetCategory.CHARACTER:
            return {
                "target_poly_count": 150000,
                "texture_resolution": "4k",
                "bake_samples": 256,
            }
        elif category == AssetCategory.ENVIRONMENT:
            return {
                "target_poly_count": 500000,
                "texture_resolution": "4k",
                "bake_samples": 128,
            }
        elif category == AssetCategory.PROP:
            return {
                "target_poly_count": 50000,
                "texture_resolution": "2k",
                "bake_samples": 128,
            }
        else:
            return {
                "target_poly_count": 100000,
                "texture_resolution": "4k",
                "bake_samples": 128,
            }

    def to_dict(self) -> Dict:
        """Export configuration as dictionary"""
        return {
            "project_root": str(self.project_root),
            "quality_preset": self.quality_preset.value,
            "directories": {
                "assets": str(self.assets_dir),
                "blender": str(self.blender_dir),
                "source": str(self.source_dir),
                "work": str(self.work_dir),
                "export": str(self.export_dir),
                "textures": str(self.textures_dir),
            },
        }


# Default global configuration instance
default_config = BlenderAssetPipelineConfig()
