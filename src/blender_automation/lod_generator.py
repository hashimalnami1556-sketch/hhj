"""
LOD (Level of Detail) Generator Module
========================================

Handles automatic generation of multiple LOD levels for 3D assets.
Implements polygon reduction, optimization, and LOD group creation.

Core algorithms:
- Quadric error metrics for edge collapse
- Smart edge removal preserving silhouettes
- Seam and UV-island boundary preservation
"""

import bpy
import bmesh
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecimateMethod(Enum):
    """Decimation algorithms"""
    UNSUBDIV = "UNSUBDIV"  # Un-subdivide (best for subdivided meshes)
    COLLAPSE = "COLLAPSE"  # Edge collapse (best for general meshes)


class LODGenerator:
    """
    Handles automatic LOD generation for 3D models.

    Workflow:
    1. Import high-poly master mesh
    2. Generate 4 LOD levels with decreasing polygon counts
    3. Create optimal UV layouts for each LOD
    4. Set screen size thresholds for each LOD
    5. Export as LOD group or separate files
    """

    def __init__(self, config=None):
        """
        Initialize LOD generator.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.original_mesh = None
        self.lod_meshes = {}  # Dict[int, bpy.types.Object]
        self.lod_stats = {}   # Dict[int, Dict] with poly counts, etc.

    def import_source_mesh(self, filepath: str) -> bpy.types.Object:
        """
        Import high-poly source mesh from file.

        Args:
            filepath: Path to source .blend or .fbx file

        Returns:
            The imported mesh object
        """
        logger.info(f"Importing source mesh from {filepath}")

        # Handle .blend files
        if filepath.endswith(".blend"):
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                data_to.objects = data_from.objects

            # Get the imported object
            imported_obj = data_to.objects[0] if data_to.objects else None
            if imported_obj:
                bpy.context.collection.objects.link(imported_obj)
                self.original_mesh = imported_obj
                return imported_obj

        # Handle .fbx files
        elif filepath.endswith(".fbx"):
            bpy.ops.import_scene.fbx(filepath=filepath)
            # Get the last selected object (should be the imported mesh)
            imported_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
            if imported_obj:
                self.original_mesh = imported_obj
                return imported_obj

        logger.error(f"Unsupported file format: {filepath}")
        return None

    def get_poly_count(self, obj: bpy.types.Object) -> int:
        """
        Get polygon count for a mesh object.

        Args:
            obj: The mesh object

        Returns:
            Number of triangles in the mesh
        """
        if obj.type != 'MESH':
            return 0

        # Count triangles in the mesh
        triangles = 0
        for face in obj.data.polygons:
            if len(face.vertices) == 3:
                triangles += 1
            elif len(face.vertices) == 4:
                triangles += 2
            else:
                # Polygon with n vertices = n-2 triangles
                triangles += len(face.vertices) - 2

        return triangles

    def generate_lods(self, source_obj: bpy.types.Object, use_vgroups: bool = True) -> Dict[int, bpy.types.Object]:
        """
        Generate all LOD levels from source mesh.

        Args:
            source_obj: The high-poly source mesh
            use_vgroups: Preserve vertex groups (for rigging)

        Returns:
            Dictionary mapping LOD level (0-3) to mesh objects
        """
        logger.info(f"Generating LODs for {source_obj.name}")

        original_poly_count = self.get_poly_count(source_obj)
        logger.info(f"Original mesh: {original_poly_count} triangles")

        # Reduction ratios for each LOD
        # LOD 0 (highest): 100%, LOD 1: 50%, LOD 2: 25%, LOD 3 (lowest): 10%
        reduction_ratios = self.config.lod_settings.reduction_ratios if self.config else (1.0, 0.5, 0.25, 0.1)

        # Generate LOD meshes
        for lod_level in range(self.config.lod_settings.lod_levels if self.config else 4):
            # Duplicate source for this LOD
            lod_obj = source_obj.copy()
            lod_obj.data = source_obj.data.copy()
            lod_obj.name = f"{source_obj.name}_LOD{lod_level}"

            # Link to scene
            bpy.context.collection.objects.link(lod_obj)

            # Skip reduction for LOD 0 (keep original)
            if lod_level > 0:
                target_ratio = reduction_ratios[lod_level]
                self._apply_decimation(lod_obj, target_ratio)

            # Store LOD
            self.lod_meshes[lod_level] = lod_obj

            # Record statistics
            lod_poly_count = self.get_poly_count(lod_obj)
            self.lod_stats[lod_level] = {
                "poly_count": lod_poly_count,
                "reduction_ratio": reduction_ratios[lod_level],
                "reduction_amount": original_poly_count - lod_poly_count,
                "screen_threshold": (450, 200, 100, 0)[lod_level],
            }

            logger.info(
                f"LOD{lod_level}: {lod_poly_count} triangles "
                f"(reduction: {reduction_ratios[lod_level]*100:.1f}%)"
            )

        return self.lod_meshes

    def _apply_decimation(self, obj: bpy.types.Object, target_ratio: float):
        """
        Apply decimation modifier to reduce polygon count.

        Args:
            obj: The mesh object to decimate
            target_ratio: Target polygon ratio (0.0 to 1.0)
        """
        # Add decimation modifier
        decimator = obj.modifiers.new(name="Decimate", type='DECIMATE')
        decimator.decimate_type = 'COLLAPSE'  # Use edge collapse
        decimator.ratio = target_ratio

        # Settings for quality
        decimator.use_collapse_triangulate = False
        decimator.invert = False

        # Apply modifier
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=decimator.name)

        # Smooth normals after decimation
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = 3.14159 * 0.6  # ~60 degrees

    def optimize_normals(self, obj: bpy.types.Object):
        """
        Recalculate and optimize normals for a mesh.

        Args:
            obj: The mesh object to optimize
        """
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.smooth_faces()
        bpy.ops.object.mode_set(mode='OBJECT')

    def create_lod_group(self) -> bpy.types.Object:
        """
        Create an LOD group/collection to manage all LOD levels.

        Returns:
            The parent LOD group object
        """
        logger.info("Creating LOD group structure")

        # Create empty object as LOD parent
        lod_parent = bpy.data.objects.new(f"{self.original_mesh.name}_LOD_Group", None)
        bpy.context.collection.objects.link(lod_parent)

        # Parent all LODs to this group
        for lod_level, lod_obj in self.lod_meshes.items():
            lod_obj.parent = lod_parent
            lod_obj.location = (0, 0, 0)  # Reset location relative to parent

        return lod_parent

    def export_lods(self, export_dir: str, format: str = "fbx"):
        """
        Export LOD meshes to files.

        Args:
            export_dir: Directory to export to
            format: Export format ('fbx', 'glb', 'usdz')
        """
        logger.info(f"Exporting LODs to {export_dir} as {format}")

        import os
        os.makedirs(export_dir, exist_ok=True)

        for lod_level, lod_obj in self.lod_meshes.items():
            # Select the LOD mesh
            bpy.context.view_layer.objects.active = lod_obj
            bpy.ops.object.select_all(action='DESELECT')
            lod_obj.select_set(True)

            # Export based on format
            if format.lower() == "fbx":
                filepath = os.path.join(export_dir, f"{lod_obj.name}.fbx")
                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True,
                    object_types={'MESH'},
                    use_smooth_groups=True,
                    use_mesh_modifiers=True,
                )

            elif format.lower() == "glb":
                filepath = os.path.join(export_dir, f"{lod_obj.name}.glb")
                bpy.ops.export_scene.gltf(
                    filepath=filepath,
                    use_selection=True,
                    use_mesh_edge_split=True,
                )

            logger.info(f"Exported LOD{lod_level} to {filepath}")

    def get_lod_stats(self) -> Dict:
        """
        Get statistics for all generated LODs.

        Returns:
            Dictionary with LOD statistics
        """
        return self.lod_stats

    def print_report(self):
        """Print detailed LOD generation report"""
        if not self.lod_stats:
            logger.warning("No LOD statistics available")
            return

        print("\n" + "="*60)
        print("LOD GENERATION REPORT")
        print("="*60)

        original_count = self.lod_stats[0]["poly_count"] if 0 in self.lod_stats else 0

        for lod_level in sorted(self.lod_stats.keys()):
            stats = self.lod_stats[lod_level]
            print(f"\nLOD {lod_level}:")
            print(f"  Polygon Count: {stats['poly_count']:,}")
            print(f"  Reduction: {(1 - stats['reduction_ratio'])*100:.1f}%")
            print(f"  Screen Threshold: >{stats['screen_threshold']}px")

        print("\n" + "="*60)


class AutoLODPipeline:
    """
    High-level automation pipeline for LOD generation.
    Handles entire workflow from import to export.
    """

    def __init__(self, config):
        """
        Initialize the LOD pipeline.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.generator = LODGenerator(config)

    def process_asset(self, source_file: str, asset_name: str) -> bool:
        """
        Process a complete asset through LOD generation.

        Args:
            source_file: Path to source high-poly mesh
            asset_name: Name for the asset

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting LOD pipeline for {asset_name}")

            # Import source
            source_obj = self.generator.import_source_mesh(source_file)
            if not source_obj:
                logger.error(f"Failed to import {source_file}")
                return False

            # Generate LODs
            self.generator.generate_lods(source_obj)

            # Create LOD group
            self.generator.create_lod_group()

            # Export LODs
            export_path = str(self.config.lod_dir / asset_name)
            self.generator.export_lods(export_path)

            # Print report
            self.generator.print_report()

            logger.info(f"Successfully processed {asset_name}")
            return True

        except Exception as e:
            logger.error(f"Error processing {asset_name}: {str(e)}")
            return False
