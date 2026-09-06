#!/usr/bin/env python3
"""
NAR Asset Production Workflow - Practical Implementation
========================================================

Complete, ready-to-run workflow for game asset production.
Demonstrates orchestrating the full pipeline with real-world patterns.

Run this file to start the asset production pipeline:
    python production_workflow.py --help
    python production_workflow.py --mode character --batch-size 5
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('asset_production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from config import BlenderAssetPipelineConfig, AssetCategory
from main import NARAssetPipeline
from batch_processor import BatchProcessingPipeline


class ProductionWorkflow:
    """
    Complete asset production workflow for NAR game development.

    Handles:
    - Asset discovery and categorization
    - Priority-based processing
    - Quality control and validation
    - Export and reporting
    - Integration with game engine
    """

    def __init__(self, project_root: str = None):
        """Initialize production workflow"""
        self.config = BlenderAssetPipelineConfig(project_root)
        self.pipeline = NARAssetPipeline()
        self.production_log = {
            "start_time": datetime.now().isoformat(),
            "assets_processed": [],
            "assets_failed": [],
            "statistics": {}
        }

    def discover_assets(self, source_dir: str) -> Dict[str, List[Path]]:
        """
        Discover and categorize assets from source directory.

        Directory structure:
        source/
        ├── characters/
        │   ├── protagonist/
        │   │   └── high_poly.blend
        │   └── npcs/
        ├── environments/
        │   ├── sky_cities/
        │   └── shattered_wastes/
        ├── props/
        └── weapons/
        """
        logger.info(f"Discovering assets in {source_dir}")

        source_path = Path(source_dir)
        discovered = {
            "character": [],
            "environment": [],
            "prop": [],
            "weapon": [],
            "vehicle": []
        }

        # Scan directory structure
        for category_dir in source_path.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name.lower()

            # Map directory names to categories
            category_map = {
                "characters": "character",
                "character": "character",
                "environments": "environment",
                "environment": "environment",
                "props": "prop",
                "prop": "prop",
                "weapons": "weapon",
                "weapon": "weapon",
                "vehicles": "vehicle",
                "vehicle": "vehicle",
            }

            category = category_map.get(category_name)
            if not category:
                continue

            # Find blend files
            for blend_file in category_dir.rglob("*.blend"):
                discovered[category].append(blend_file)

        # Log discovery results
        for category, files in discovered.items():
            if files:
                logger.info(f"  {category}: {len(files)} assets")

        return discovered

    def prioritize_assets(self, discovered: Dict[str, List[Path]]) -> List[tuple]:
        """
        Create priority queue for asset processing.

        Priority rules:
        1. Characters (hero > npcs > generic)
        2. Environments (critical > secondary)
        3. Weapons/props (used > unused)
        4. Quality improves as more assets are processed
        """
        queue = []

        # Characters (highest priority)
        for asset in discovered["character"]:
            priority = self._calculate_priority(asset, "character")
            queue.append((priority, "character", asset))

        # Environments
        for asset in discovered["environment"]:
            priority = self._calculate_priority(asset, "environment")
            queue.append((priority, "environment", asset))

        # Props and weapons
        for asset in discovered["prop"]:
            priority = self._calculate_priority(asset, "prop")
            queue.append((priority, "prop", asset))

        for asset in discovered["weapon"]:
            priority = self._calculate_priority(asset, "weapon")
            queue.append((priority, "weapon", asset))

        # Sort by priority (lower = higher priority)
        queue.sort(key=lambda x: x[0])

        return queue

    def _calculate_priority(self, asset_path: Path, category: str) -> int:
        """Calculate priority score for asset"""
        score = 0

        name = asset_path.stem.lower()

        # Hero/main assets get highest priority
        if any(hero in name for hero in ["protagonist", "naris", "main"]):
            score = 1
        # NPCs next
        elif "npc" in name:
            score = 2
        # Generic last
        else:
            score = 3

        # Bosses get high priority
        if "boss" in name:
            score = 1

        # Rare/special assets prioritized
        if "legendary" in name or "unique" in name:
            score = 1

        return score

    def process_batch(
        self,
        assets: List[tuple],
        batch_size: int = 5,
        max_threads: int = 4
    ) -> Dict:
        """
        Process batch of assets through production pipeline.

        Args:
            assets: List of (priority, category, path) tuples
            batch_size: Number of assets per batch
            max_threads: Maximum processing threads

        Returns:
            Production results
        """
        logger.info(f"Starting batch processing ({len(assets)} assets)")

        results = {
            "batches": [],
            "total_processed": 0,
            "total_failed": 0,
            "start_time": datetime.now().isoformat()
        }

        # Process in batches
        for batch_idx in range(0, len(assets), batch_size):
            batch = assets[batch_idx:batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1

            logger.info(f"\n{'='*60}")
            logger.info(f"BATCH {batch_num} - {len(batch)} assets")
            logger.info(f"{'='*60}")

            batch_results = self._process_batch_group(batch, max_threads)
            results["batches"].append(batch_results)
            results["total_processed"] += batch_results["processed"]
            results["total_failed"] += batch_results["failed"]

            # Update production log
            for asset_result in batch_results.get("assets", []):
                if asset_result["status"] == "success":
                    self.production_log["assets_processed"].append(asset_result)
                else:
                    self.production_log["assets_failed"].append(asset_result)

        results["end_time"] = datetime.now().isoformat()
        return results

    def _process_batch_group(self, batch: List[tuple], max_threads: int) -> Dict:
        """Process a single batch group"""
        results = {
            "processed": 0,
            "failed": 0,
            "assets": []
        }

        for idx, (priority, category, asset_path) in enumerate(batch, 1):
            logger.info(f"\n[{idx}/{len(batch)}] Processing: {asset_path.name}")
            logger.info(f"  Category: {category} | Priority: {priority}")

            asset_name = asset_path.stem

            try:
                # Process through pipeline
                success = self.pipeline.process_single_asset(
                    source_file=str(asset_path),
                    asset_name=asset_name,
                    asset_category=category,
                    stages=['retopo', 'lod', 'uv', 'pbr', 'export']
                )

                if success:
                    logger.info(f"  ✓ Successfully processed {asset_name}")
                    results["processed"] += 1
                    results["assets"].append({
                        "name": asset_name,
                        "category": category,
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"  ✗ Failed to process {asset_name}")
                    results["failed"] += 1
                    results["assets"].append({
                        "name": asset_name,
                        "category": category,
                        "status": "failed",
                        "error": "Pipeline processing failed",
                        "timestamp": datetime.now().isoformat()
                    })

            except Exception as e:
                logger.error(f"  ✗ Exception processing {asset_name}: {str(e)}")
                results["failed"] += 1
                results["assets"].append({
                    "name": asset_name,
                    "category": category,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        return results

    def generate_quality_report(self, results: Dict) -> str:
        """Generate quality assurance report"""
        report = "\n" + "="*60 + "\n"
        report += "PRODUCTION QUALITY REPORT\n"
        report += "="*60 + "\n\n"

        total = results["total_processed"] + results["total_failed"]
        success_rate = (results["total_processed"] / total * 100) if total > 0 else 0

        report += f"Total Assets: {total}\n"
        report += f"Successfully Processed: {results['total_processed']}\n"
        report += f"Failed: {results['total_failed']}\n"
        report += f"Success Rate: {success_rate:.1f}%\n\n"

        # Batch summary
        report += "Batch Summary:\n"
        for batch_num, batch in enumerate(results["batches"], 1):
            report += f"  Batch {batch_num}: {batch['processed']} ✓ / {batch['failed']} ✗\n"

        # Failed assets
        if self.production_log["assets_failed"]:
            report += "\nFailed Assets:\n"
            for asset in self.production_log["assets_failed"]:
                report += f"  - {asset['name']}: {asset.get('error', 'Unknown error')}\n"

        report += "\n" + "="*60 + "\n"
        return report

    def export_production_log(self, output_file: str = "production_log.json"):
        """Export complete production log"""
        self.production_log["end_time"] = datetime.now().isoformat()
        self.production_log["duration_seconds"] = (
            datetime.fromisoformat(self.production_log["end_time"]) -
            datetime.fromisoformat(self.production_log["start_time"])
        ).total_seconds()

        with open(output_file, 'w') as f:
            json.dump(self.production_log, f, indent=2)

        logger.info(f"Production log exported to {output_file}")

    def run_production_cycle(
        self,
        source_dir: str,
        asset_category: Optional[str] = None,
        batch_size: int = 5,
        max_threads: int = 4
    ) -> Dict:
        """
        Execute complete production cycle.

        Args:
            source_dir: Source assets directory
            asset_category: Specific category to process (or None for all)
            batch_size: Assets per batch
            max_threads: Processing threads

        Returns:
            Complete production results
        """
        logger.info("="*60)
        logger.info("NAR ASSET PRODUCTION CYCLE")
        logger.info("="*60)

        # Phase 1: Discovery
        logger.info("\nPhase 1: Asset Discovery...")
        discovered = self.discover_assets(source_dir)

        # Filter by category if specified
        if asset_category:
            for cat in list(discovered.keys()):
                if cat != asset_category:
                    discovered[cat] = []

        total_assets = sum(len(assets) for assets in discovered.values())
        if total_assets == 0:
            logger.error("No assets found!")
            return {"status": "failed", "reason": "No assets found"}

        logger.info(f"Discovered {total_assets} assets total")

        # Phase 2: Prioritization
        logger.info("\nPhase 2: Asset Prioritization...")
        queue = self.prioritize_assets(discovered)
        logger.info(f"Queue created with {len(queue)} assets")

        # Phase 3: Processing
        logger.info("\nPhase 3: Asset Processing...")
        results = self.process_batch(queue, batch_size, max_threads)

        # Phase 4: Quality Report
        logger.info("\nPhase 4: Quality Report...")
        report = self.generate_quality_report(results)
        logger.info(report)

        # Phase 5: Export Log
        logger.info("\nPhase 5: Export Production Log...")
        self.export_production_log()

        logger.info("\n✓ Production cycle complete!")
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NAR Asset Production Workflow"
    )

    parser.add_argument(
        '--source-dir',
        default='./assets/source',
        help='Source assets directory'
    )

    parser.add_argument(
        '--mode',
        '--category',
        choices=['character', 'environment', 'prop', 'weapon', 'all'],
        default='all',
        help='Asset category to process'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Assets per batch'
    )

    parser.add_argument(
        '--threads',
        type=int,
        default=4,
        help='Maximum processing threads'
    )

    parser.add_argument(
        '--project-root',
        help='Project root directory'
    )

    args = parser.parse_args()

    # Initialize workflow
    workflow = ProductionWorkflow(args.project_root)

    # Run production cycle
    asset_category = None if args.mode == 'all' else args.mode

    results = workflow.run_production_cycle(
        source_dir=args.source_dir,
        asset_category=asset_category,
        batch_size=args.batch_size,
        max_threads=args.threads
    )

    return 0 if results.get("status") != "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
