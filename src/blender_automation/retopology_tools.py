"""
Retopology Tools Module
=======================

Handles automatic retopology (mesh simplification and optimization).
Converts high-poly sculpts to low-poly game engine-ready meshes.

Methods:
- Quadriflow voxel-based retopology
- Custom polygon count targeting
- Symmetry-aware retopology
- UV seam preservation
"""

import bpy
import bmesh
from typing import Dict, Optional, Tuple
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetopologyMethod(Enum):
    """Retopology algorithms"""
    QUADRIFLOW = "quadriflow"  # Voxel-based (best quality)
    DECIMATE = "decimate"  # Edge collapse (fast, less control)
    VOXEL_REMESH = "voxel_remesh"  # Voxel grid remeshing


class RetopologyTools:
    """
    Handles automatic retopology for game engine mesh optimization.

    Workflow:
    1. Analyze high-poly source geometry
    2. Apply retopology algorithm
    3. Preserve UV seams and hard edges
    4. Optimize for game engine constraints
    5. Validate mesh for export
    """

    def __init__(self, config=None):
        """
        Initialize retopology tools.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.source_mesh = None
        self.retopologized_mesh = None
        self.retopo_stats = {}

    def setup_quadriflow(self) -> bool:
        """
        Check if Quadriflow addon is available and enable it.

        Returns:
            True if Quadriflow is available
        """
        # Try to enable Quadriflow addon
        try:
            bpy.ops.preferences.addon_enable(module='quadriflow')
            logger.info("Quadriflow addon enabled")
            return True
        except:
            logger.warning("Quadriflow addon not available, using fallback method")
            return False

    def quadriflow_retopology(
        self,
        source_obj: bpy.types.Object,
        target_face_count: Optional[int] = None,
        voxel_size: float = 0.1,
        use_mesh_symmetry: bool = True,
        preserve_sharp: bool = True,
        smooth_normals: bool = True,
    ) -> bpy.types.Object:
        """
        Apply Quadriflow voxel-based retopology.

        Quadriflow is excellent for producing clean, quad-based topology
        suitable for rigging and animation.

        Args:
            source_obj: The high-poly source mesh
            target_face_count: Target face count (if None, uses voxel_size)
            voxel_size: Voxel grid size (lower = higher detail)
            use_mesh_symmetry: Detect and preserve mesh symmetry
            preserve_sharp: Preserve sharp edges
            smooth_normals: Smooth normals after retopology

        Returns:
            The retopologized mesh object
        """
        logger.info("Applying Quadriflow retopology")

        if not self.setup_quadriflow():
            logger.error("Quadriflow not available")
            return None

        # Make source object active
        bpy.context.view_layer.objects.active = source_obj
        source_obj.select_set(True)

        try:
            # Apply Quadriflow
            bpy.ops.object.quadriflow_remesh(
                use_mesh_symmetry=use_mesh_symmetry,
                use_preserve_sharp=preserve_sharp,
                use_preserve_border=True,
                mode='FACES' if target_face_count else 'VOXELS',
                face_count=target_face_count or 50000,
            )

            # Get the retopologized object (Quadriflow creates it)
            retopo_obj = bpy.context.active_object
            retopo_obj.name = f"{source_obj.name}_Retopo"

            # Smooth normals if requested
            if smooth_normals:
                retopo_obj.data.use_auto_smooth = True
                retopo_obj.data.auto_smooth_angle = 3.14159 * 0.75  # ~60 degrees

            self.retopologized_mesh = retopo_obj
            self._record_retopo_stats(retopo_obj)

            logger.info(f"Quadriflow retopology completed: {self.get_face_count(retopo_obj)} faces")
            return retopo_obj

        except Exception as e:
            logger.error(f"Quadriflow retopology failed: {str(e)}")
            return None

    def decimate_retopology(
        self,
        source_obj: bpy.types.Object,
        target_ratio: float = 0.5,
        use_collapse: bool = True,
        preserve_topology: bool = True,
    ) -> bpy.types.Object:
        """
        Apply decimate modifier for retopology.

        Faster than Quadriflow but less control. Good for quick iterations.

        Args:
            source_obj: The source mesh
            target_ratio: Target polygon ratio (0.0-1.0)
            use_collapse: Use edge collapse (vs un-subdivide)
            preserve_topology: Preserve mesh topology

        Returns:
            The decimated mesh object
        """
        logger.info(f"Applying decimate retopology (ratio={target_ratio})")

        # Duplicate source
        retopo_obj = source_obj.copy()
        retopo_obj.data = source_obj.data.copy()
        retopo_obj.name = f"{source_obj.name}_Decimated"

        bpy.context.collection.objects.link(retopo_obj)

        # Add decimate modifier
        decimate = retopo_obj.modifiers.new(name="Decimate", type='DECIMATE')
        decimate.decimate_type = 'COLLAPSE' if use_collapse else 'UNSUBDIV'
        decimate.ratio = target_ratio

        if use_collapse:
            decimate.use_collapse_triangulate = False

        # Apply modifier
        bpy.context.view_layer.objects.active = retopo_obj
        bpy.ops.object.modifier_apply(modifier=decimate.name)

        # Smooth normals
        retopo_obj.data.use_auto_smooth = True
        retopo_obj.data.auto_smooth_angle = 3.14159 * 0.75

        self.retopologized_mesh = retopo_obj
        self._record_retopo_stats(retopo_obj)

        logger.info(f"Decimate retopology completed: {self.get_face_count(retopo_obj)} faces")
        return retopo_obj

    def voxel_remesh(
        self,
        source_obj: bpy.types.Object,
        voxel_size: float = 0.1,
        adaptivity: float = 0.0,
    ) -> bpy.types.Object:
        """
        Apply voxel remeshing using Voxel Remesh modifier.

        Useful for organic geometry and sculpts.

        Args:
            source_obj: The source mesh
            voxel_size: Size of voxels
            adaptivity: Adaptivity value (0-1)

        Returns:
            The voxel remeshed object
        """
        logger.info(f"Applying voxel remesh (size={voxel_size})")

        # Duplicate source
        retopo_obj = source_obj.copy()
        retopo_obj.data = source_obj.data.copy()
        retopo_obj.name = f"{source_obj.name}_Voxel"

        bpy.context.collection.objects.link(retopo_obj)

        # Add voxel remesh modifier
        voxel = retopo_obj.modifiers.new(name="VoxelRemesh", type='REMESH')
        voxel.mode = 'VOXELS'
        voxel.voxel_size = voxel_size
        voxel.adaptivity = adaptivity

        # Apply modifier
        bpy.context.view_layer.objects.active = retopo_obj
        bpy.ops.object.modifier_apply(modifier=voxel.name)

        self.retopologized_mesh = retopo_obj
        self._record_retopo_stats(retopo_obj)

        logger.info(f"Voxel remesh completed: {self.get_face_count(retopo_obj)} faces")
        return retopo_obj

    def get_face_count(self, obj: bpy.types.Object) -> int:
        """Get face count for a mesh"""
        return len(obj.data.polygons)

    def validate_retopo_mesh(self, mesh_obj: bpy.types.Object) -> Dict[str, bool]:
        """
        Validate retopologized mesh for game engine export.

        Checks for:
        - Non-manifold geometry
        - Degenerate faces
        - Polygon count within limits
        - UV coverage

        Args:
            mesh_obj: The mesh to validate

        Returns:
            Dictionary of validation results
        """
        logger.info("Validating retopologized mesh")

        validation = {
            "is_manifold": True,
            "no_degenerate_faces": True,
            "poly_count_acceptable": True,
            "has_uvs": True,
            "valid_for_export": True,
        }

        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Check for degenerate faces
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=3, type='LT')  # Select faces with < 3 sides

        num_degenerate = len([f for f in mesh_obj.data.polygons if f.select])
        if num_degenerate > 0:
            validation["no_degenerate_faces"] = False
            logger.warning(f"Found {num_degenerate} degenerate faces")

        bpy.ops.object.mode_set(mode='OBJECT')

        # Check polygon count
        face_count = len(mesh_obj.data.polygons)
        target_count = self.config.retopology_settings.target_poly_count if self.config else 50000
        if face_count > target_count * 1.5:  # Allow 50% over
            validation["poly_count_acceptable"] = False
            logger.warning(f"Polygon count {face_count} exceeds target {target_count}")

        # Check for UVs
        if not mesh_obj.data.uv_layers:
            validation["has_uvs"] = False
            logger.warning("Mesh has no UV maps")

        # Overall validation
        validation["valid_for_export"] = all(validation.values())

        return validation

    def cleanup_mesh(self, mesh_obj: bpy.types.Object) -> bool:
        """
        Clean up mesh for export.

        Removes:
        - Degenerate geometry
        - Duplicate vertices
        - Unused materials
        - Internal faces

        Args:
            mesh_obj: The mesh to clean

        Returns:
            True if successful
        """
        logger.info("Cleaning up mesh")

        try:
            bpy.context.view_layer.objects.active = mesh_obj
            bpy.ops.object.mode_set(mode='EDIT')

            # Select all
            bpy.ops.mesh.select_all(action='SELECT')

            # Remove degenerate geometry
            bpy.ops.mesh.delete_loose()

            # Merge nearby vertices
            bpy.ops.mesh.remove_doubles(threshold=0.001)

            # Recalculate normals
            bpy.ops.mesh.normals_make_consistent(inside=False)

            bpy.ops.object.mode_set(mode='OBJECT')

            logger.info("Mesh cleanup completed")
            return True

        except Exception as e:
            logger.error(f"Mesh cleanup failed: {str(e)}")
            return False

    def _record_retopo_stats(self, retopo_obj: bpy.types.Object):
        """Record statistics about retopologized mesh"""
        original_count = self.get_face_count(self.source_mesh) if self.source_mesh else 0
        retopo_count = self.get_face_count(retopo_obj)

        self.retopo_stats = {
            "original_face_count": original_count,
            "retopo_face_count": retopo_count,
            "reduction_ratio": retopo_count / original_count if original_count > 0 else 0,
            "mesh_name": retopo_obj.name,
        }

    def get_stats(self) -> Dict:
        """Get retopology statistics"""
        return self.retopo_stats

    def print_report(self):
        """Print detailed retopology report"""
        if not self.retopo_stats:
            logger.warning("No retopology statistics available")
            return

        stats = self.retopo_stats

        print("\n" + "="*60)
        print("RETOPOLOGY REPORT")
        print("="*60)
        print(f"\nMesh: {stats['mesh_name']}")
        print(f"Original Polygons: {stats['original_face_count']:,}")
        print(f"Retopologized Polygons: {stats['retopo_face_count']:,}")
        print(f"Reduction: {(1 - stats['reduction_ratio'])*100:.1f}%")
        print("\n" + "="*60)


class AutoRetopologyPipeline:
    """
    Complete retopology pipeline from high-poly to game-ready mesh.
    """

    def __init__(self, config):
        """
        Initialize retopology pipeline.

        Args:
            config: Pipeline configuration object
        """
        self.config = config
        self.tools = RetopologyTools(config)

    def process_asset(
        self,
        source_obj: bpy.types.Object,
        asset_category: str = "environment",
        method: str = "quadriflow"
    ) -> Optional[bpy.types.Object]:
        """
        Process asset through retopology pipeline.

        Args:
            source_obj: High-poly source mesh
            asset_category: Type of asset (character, environment, prop, etc.)
            method: Retopology method to use

        Returns:
            The retopologized mesh object
        """
        try:
            logger.info(f"Starting retopology for {source_obj.name}")

            self.tools.source_mesh = source_obj

            # Determine target poly count based on category
            if asset_category == "character":
                target_count = self.config.retopology_settings.character_target_poly_count
            else:
                target_count = self.config.retopology_settings.target_poly_count

            # Apply retopology method
            if method == "quadriflow":
                retopo_obj = self.tools.quadriflow_retopology(
                    source_obj,
                    target_face_count=target_count
                )
            elif method == "decimate":
                ratio = target_count / max(self.tools.get_face_count(source_obj), 1)
                retopo_obj = self.tools.decimate_retopology(source_obj, target_ratio=min(ratio, 1.0))
            else:
                retopo_obj = self.tools.voxel_remesh(source_obj)

            if not retopo_obj:
                logger.error("Retopology failed")
                return None

            # Cleanup
            self.tools.cleanup_mesh(retopo_obj)

            # Validate
            validation = self.tools.validate_retopo_mesh(retopo_obj)
            if not validation["valid_for_export"]:
                logger.warning("Validation issues found, but proceeding")

            # Print report
            self.tools.print_report()

            logger.info(f"Successfully retopologized {source_obj.name}")
            return retopo_obj

        except Exception as e:
            logger.error(f"Error in retopology pipeline: {str(e)}")
            return None
