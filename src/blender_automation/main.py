#!/usr/bin/env python3
"""
Blender Asset Automation Main Orchestration Script
===================================================

Complete asset pipeline orchestration for NARIS game development.
Handles LOD generation, retopology, PBR baking, UV automation, and batch processing.

Usage:
    blender --background --python main.py -- --asset character --input path/to/source.blend

Or within Blender:
    exec(open("main.py").read())
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import pipeline modules
from config import BlenderAssetPipelineConfig, AssetCategory
from lod_generator import AutoLODPipeline
from pbr_baker import HighPolyBakerPipeline
from uv_automation import AutoUVPipeline
from retopology_tools import AutoRetopologyPipeline
from batch_processor import BatchProcessingPipeline


class NARAssetPipeline:
    """
    Main asset production pipeline for NAR: Chronicles of the Fallen Star.

    Orchestrates the complete workflow from high-poly source to game-ready asset.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the pipeline.

        Args:
            config_path: Path to custom configuration (optional)
        """
        self.config = BlenderAssetPipelineConfig(config_path)
        self.lod_pipeline = AutoLODPipeline(self.config)
        self.retopo_pipeline = AutoRetopologyPipeline(self.config)
        self.pbr_pipeline = HighPolyBakerPipeline(self.config)
        self.uv_pipeline = AutoUVPipeline(self.config)
        self.batch_pipeline = BatchProcessingPipeline(self.config)

        logger.info("NAR Asset Pipeline initialized")

    def process_single_asset(
        self,
        source_file: str,
        asset_name: str,
        asset_category: str = "environment",
        stages: Optional[list] = None
    ) -> bool:
        """
        Process a single asset through the complete pipeline.

        Args:
            source_file: Path to source high-poly mesh
            asset_name: Name for the asset
            asset_category: Asset type (character, environment, prop, vehicle, weapon)
            stages: List of pipeline stages to run (default: all)
                  Options: ['lod', 'retopo', 'pbr', 'uv', 'export']

        Returns:
            True if successful
        """
        if stages is None:
            stages = ['retopo', 'lod', 'uv', 'pbr', 'export']

        logger.info(f"Processing {asset_name} ({asset_category})")
        logger.info(f"Stages: {', '.join(stages)}")

        try:
            import bpy

            # Clear scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

            # === STAGE 1: Retopology (high-poly to low-poly) ===
            if 'retopo' in stages:
                logger.info("Stage 1: Retopology")

                # Import high-poly source
                if source_file.endswith('.blend'):
                    with bpy.data.libraries.load(source_file) as (data_from, data_to):
                        data_to.objects = data_from.objects

                    highpoly_obj = data_to.objects[0] if data_to.objects else None
                    if highpoly_obj:
                        bpy.context.collection.objects.link(highpoly_obj)
                else:
                    bpy.ops.import_scene.fbx(filepath=source_file)
                    highpoly_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None

                if highpoly_obj:
                    lowpoly_obj = self.retopo_pipeline.process_asset(
                        highpoly_obj,
                        asset_category=asset_category
                    )
                    if not lowpoly_obj:
                        logger.error("Retopology failed")
                        return False
                else:
                    logger.error(f"Failed to import {source_file}")
                    return False

            # === STAGE 2: LOD Generation ===
            if 'lod' in stages:
                logger.info("Stage 2: LOD Generation")

                if 'retopo' not in stages:
                    # Import source if not already done
                    bpy.ops.import_scene.fbx(filepath=source_file)
                    lowpoly_obj = bpy.context.selected_objects[0]

                self.lod_pipeline.generator.original_mesh = lowpoly_obj
                lods = self.lod_pipeline.generator.generate_lods(lowpoly_obj)
                self.lod_pipeline.generator.create_lod_group()

                export_path = str(self.config.export_dir / asset_name / "lods")
                self.lod_pipeline.generator.export_lods(export_path, format="fbx")

            # === STAGE 3: UV Automation ===
            if 'uv' in stages:
                logger.info("Stage 3: UV Automation")

                bpy.context.view_layer.objects.active = lowpoly_obj
                self.uv_pipeline.process_asset(lowpoly_obj, generate_lightmap=True)

            # === STAGE 4: PBR Baking ===
            if 'pbr' in stages:
                logger.info("Stage 4: PBR Baking")

                self.pbr_pipeline.baker.setup_baking_scene(lowpoly_obj)
                self.pbr_pipeline.baker.create_bake_materials(lowpoly_obj)
                self.pbr_pipeline.baker.bake_textures()

                export_path = str(self.config.pbr_dir / asset_name)
                self.pbr_pipeline.baker.export_baked_textures(export_path, format="EXR")

            # === STAGE 5: Export ===
            if 'export' in stages:
                logger.info("Stage 5: Export")

                export_path = str(self.config.export_dir / asset_name)
                os.makedirs(export_path, exist_ok=True)

                # Export low-poly mesh
                bpy.context.view_layer.objects.active = lowpoly_obj
                bpy.ops.object.select_all(action='DESELECT')
                lowpoly_obj.select_set(True)

                export_file = os.path.join(export_path, f"{asset_name}.fbx")
                bpy.ops.export_scene.fbx(
                    filepath=export_file,
                    use_selection=True,
                    object_types={'MESH'},
                )

                logger.info(f"Exported to {export_file}")

            logger.info(f"Successfully processed {asset_name}")
            return True

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def process_batch(
        self,
        source_directory: str,
        asset_category: str = "environment",
        num_threads: int = 4
    ) -> Dict:
        """
        Process multiple assets in batch mode.

        Args:
            source_directory: Directory containing source assets
            asset_category: Category for all assets
            num_threads: Number of parallel processing threads

        Returns:
            Processing report
        """
        logger.info(f"Starting batch processing from {source_directory}")

        pipeline = BatchProcessingPipeline(self.config, num_threads)
        return pipeline.process_assets(
            source_directory,
            asset_category=asset_category,
            output_directory=str(self.config.export_dir)
        )

    def print_config(self):
        """Print current pipeline configuration"""
        print("\n" + "="*60)
        print("NAR ASSET PIPELINE CONFIGURATION")
        print("="*60)

        config_dict = self.config.to_dict()

        for key, value in config_dict.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

        print("\n" + "="*60)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="NAR Asset Pipeline - Blender Automation Framework"
    )

    parser.add_argument(
        '--mode',
        choices=['single', 'batch', 'info'],
        default='single',
        help='Processing mode (default: single)'
    )

    parser.add_argument(
        '--input', '-i',
        required=False,
        help='Input file or directory path'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output directory path'
    )

    parser.add_argument(
        '--asset-name',
        help='Asset name (for single mode)'
    )

    parser.add_argument(
        '--asset-category',
        choices=['character', 'environment', 'prop', 'vehicle', 'weapon', 'architectural'],
        default='environment',
        help='Asset category'
    )

    parser.add_argument(
        '--stages',
        nargs='+',
        choices=['lod', 'retopo', 'pbr', 'uv', 'export'],
        default=['retopo', 'lod', 'uv', 'pbr', 'export'],
        help='Pipeline stages to run'
    )

    parser.add_argument(
        '--threads',
        type=int,
        default=4,
        help='Number of processing threads (for batch mode)'
    )

    parser.add_argument(
        '--config',
        help='Path to custom configuration file'
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()

    # Initialize pipeline
    pipeline = NARAssetPipeline(args.config)

    # Print configuration for info mode
    if args.mode == 'info':
        pipeline.print_config()
        return

    # Single asset processing
    elif args.mode == 'single':
        if not args.input or not args.asset_name:
            logger.error("Single mode requires --input and --asset-name")
            return

        success = pipeline.process_single_asset(
            source_file=args.input,
            asset_name=args.asset_name,
            asset_category=args.asset_category,
            stages=args.stages
        )

        if success:
            logger.info("✓ Processing completed successfully")
        else:
            logger.error("✗ Processing failed")

    # Batch processing
    elif args.mode == 'batch':
        if not args.input:
            logger.error("Batch mode requires --input (directory)")
            return

        report = pipeline.process_batch(
            source_directory=args.input,
            asset_category=args.asset_category,
            num_threads=args.threads
        )

        logger.info(f"Batch processing completed: {report['summary']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
