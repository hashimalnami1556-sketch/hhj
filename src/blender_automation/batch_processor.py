"""
Batch Processing Module
=======================

Orchestrates batch processing of multiple assets through the entire pipeline.
Handles parallel processing, error recovery, and progress reporting.

Features:
- Multi-threaded processing
- Queue-based workflow management
- Error handling and recovery
- Progress reporting and logging
- Automated report generation
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import threading
from queue import Queue
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status of batch processing tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AssetTask:
    """Individual asset processing task"""
    asset_id: str
    asset_name: str
    source_file: str
    asset_category: str
    priority: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    output_files: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['output_files'] = self.output_files or []
        return data

    def get_duration(self) -> float:
        """Get processing duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class BatchProcessor:
    """
    Orchestrates batch processing of multiple assets.

    Workflow:
    1. Queue assets for processing
    2. Process queue with multiple threads
    3. Apply LOD generation, retopology, baking, UV automation
    4. Export to target formats
    5. Generate comprehensive report
    """

    def __init__(self, config, num_threads: int = 4):
        """
        Initialize batch processor.

        Args:
            config: Pipeline configuration object
            num_threads: Number of processing threads
        """
        self.config = config
        self.num_threads = num_threads
        self.task_queue = Queue()
        self.completed_tasks = []
        self.failed_tasks = []
        self.processing_threads = []
        self.is_running = False
        self.total_start_time = None

    def add_task(self, task: AssetTask) -> bool:
        """
        Add an asset to the processing queue.

        Args:
            task: The asset task to add

        Returns:
            True if added successfully
        """
        logger.info(f"Added task: {task.asset_name} (priority: {task.priority})")
        self.task_queue.put(task)
        return True

    def add_tasks_from_directory(self, source_dir: str, asset_category: str = "environment"):
        """
        Add all assets from a directory to the queue.

        Args:
            source_dir: Directory containing source files
            asset_category: Category for all assets in directory
        """
        source_path = Path(source_dir)

        # Supported formats
        supported_formats = {'.blend', '.fbx', '.obj', '.gltf', '.glb'}

        asset_counter = 0
        for file in source_path.glob('*'):
            if file.suffix.lower() in supported_formats:
                asset_id = f"asset_{asset_counter:04d}"
                asset_name = file.stem
                task = AssetTask(
                    asset_id=asset_id,
                    asset_name=asset_name,
                    source_file=str(file),
                    asset_category=asset_category,
                    priority=0
                )
                self.add_task(task)
                asset_counter += 1

        logger.info(f"Queued {asset_counter} assets from {source_dir}")

    def process_queue(self, processors: Dict[str, Callable]) -> Dict:
        """
        Process all queued tasks.

        Args:
            processors: Dictionary mapping processor names to functions

        Returns:
            Processing report
        """
        logger.info(f"Starting batch processing with {self.num_threads} threads")

        self.is_running = True
        self.total_start_time = time.time()

        # Start worker threads
        for i in range(self.num_threads):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(i, processors),
                daemon=True
            )
            thread.start()
            self.processing_threads.append(thread)

        # Wait for queue to be empty
        self.task_queue.join()

        # Signal threads to stop
        self.is_running = False

        # Wait for all threads to finish
        for thread in self.processing_threads:
            thread.join()

        total_time = time.time() - self.total_start_time

        logger.info(f"Batch processing completed in {total_time:.2f} seconds")

        return self.generate_report(total_time)

    def _worker_thread(self, thread_id: int, processors: Dict[str, Callable]):
        """
        Worker thread that processes tasks from the queue.

        Args:
            thread_id: ID of this thread
            processors: Dictionary of processor functions
        """
        logger.info(f"Worker thread {thread_id} started")

        while self.is_running:
            try:
                # Get task with timeout to allow graceful shutdown
                task = self.task_queue.get(timeout=1)

                if task is None:
                    break

                self._process_task(task, processors)
                self.task_queue.task_done()

            except:
                # Timeout - continue
                continue

    def _process_task(self, task: AssetTask, processors: Dict[str, Callable]):
        """
        Process a single asset task.

        Args:
            task: The asset task to process
            processors: Dictionary of processor functions
        """
        task.status = ProcessingStatus.IN_PROGRESS
        task.start_time = time.time()

        logger.info(f"Processing {task.asset_name}...")

        try:
            output_files = []

            # Run through processors
            for processor_name, processor_func in processors.items():
                logger.info(f"  [{processor_name}] Processing {task.asset_name}")

                try:
                    result = processor_func(task.source_file, task)
                    if result:
                        if isinstance(result, list):
                            output_files.extend(result)
                        else:
                            output_files.append(result)

                except Exception as e:
                    logger.error(f"  [{processor_name}] Failed: {str(e)}")
                    raise

            task.status = ProcessingStatus.COMPLETED
            task.output_files = output_files
            self.completed_tasks.append(task)

            logger.info(f"Successfully processed {task.asset_name}")

        except Exception as e:
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            self.failed_tasks.append(task)

            logger.error(f"Failed to process {task.asset_name}: {str(e)}")

        finally:
            task.end_time = time.time()

    def generate_report(self, total_time: float) -> Dict:
        """
        Generate comprehensive processing report.

        Args:
            total_time: Total processing time in seconds

        Returns:
            Report dictionary
        """
        logger.info("Generating processing report")

        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        success_rate = (len(self.completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_processing_time": total_time,
            "summary": {
                "total_tasks": total_tasks,
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "success_rate": success_rate,
            },
            "completed_tasks": [task.to_dict() for task in self.completed_tasks],
            "failed_tasks": [task.to_dict() for task in self.failed_tasks],
            "performance": self._calculate_performance_metrics(),
        }

        return report

    def _calculate_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.completed_tasks:
            return {}

        durations = [task.get_duration() for task in self.completed_tasks if task.get_duration() > 0]

        if not durations:
            return {}

        return {
            "average_task_time": sum(durations) / len(durations),
            "fastest_task": min(durations),
            "slowest_task": max(durations),
            "tasks_per_second": len(self.completed_tasks) / sum(durations) if sum(durations) > 0 else 0,
        }

    def save_report(self, output_path: str):
        """
        Save processing report to file.

        Args:
            output_path: Path to save report
        """
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tasks": len(self.completed_tasks) + len(self.failed_tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
            },
            "completed_tasks": [task.to_dict() for task in self.completed_tasks],
            "failed_tasks": [task.to_dict() for task in self.failed_tasks],
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Report saved to {output_path}")

    def print_summary(self):
        """Print processing summary"""
        total = len(self.completed_tasks) + len(self.failed_tasks)
        success_rate = (len(self.completed_tasks) / total * 100) if total > 0 else 0

        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"\nTotal Tasks: {total}")
        print(f"Completed: {len(self.completed_tasks)}")
        print(f"Failed: {len(self.failed_tasks)}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.completed_tasks:
            durations = [t.get_duration() for t in self.completed_tasks if t.get_duration() > 0]
            if durations:
                print(f"\nPerformance:")
                print(f"  Average Time: {sum(durations)/len(durations):.2f}s")
                print(f"  Total Time: {sum(durations):.2f}s")

        if self.failed_tasks:
            print(f"\nFailed Tasks:")
            for task in self.failed_tasks:
                print(f"  - {task.asset_name}: {task.error_message}")

        print("\n" + "="*60)


class BatchProcessingPipeline:
    """
    High-level API for batch asset processing.
    """

    def __init__(self, config, num_threads: int = 4):
        """
        Initialize batch pipeline.

        Args:
            config: Pipeline configuration object
            num_threads: Number of processing threads
        """
        self.config = config
        self.processor = BatchProcessor(config, num_threads)

    def process_assets(
        self,
        source_directory: str,
        asset_category: str = "environment",
        output_directory: Optional[str] = None
    ) -> Dict:
        """
        Process all assets in a directory.

        Args:
            source_directory: Source asset directory
            asset_category: Asset category for all assets
            output_directory: Output directory for processed assets

        Returns:
            Processing report
        """
        logger.info(f"Starting batch processing for {asset_category} assets")

        # Add tasks from directory
        self.processor.add_tasks_from_directory(source_directory, asset_category)

        # Define processors
        processors = {
            "lod_generation": self._process_lod,
            "retopology": self._process_retopology,
            "pbr_baking": self._process_pbr,
            "uv_automation": self._process_uvs,
        }

        # Process queue
        report = self.processor.process_queue(processors)

        # Print summary
        self.processor.print_summary()

        # Save report
        if output_directory:
            report_path = os.path.join(output_directory, "processing_report.json")
            self.processor.save_report(report_path)

        return report

    def _process_lod(self, source_file: str, task: AssetTask) -> Optional[str]:
        """LOD generation processor"""
        # Placeholder for LOD generation logic
        logger.info(f"LOD generation for {task.asset_name}")
        return None

    def _process_retopology(self, source_file: str, task: AssetTask) -> Optional[str]:
        """Retopology processor"""
        # Placeholder for retopology logic
        logger.info(f"Retopology for {task.asset_name}")
        return None

    def _process_pbr(self, source_file: str, task: AssetTask) -> Optional[str]:
        """PBR baking processor"""
        # Placeholder for PBR baking logic
        logger.info(f"PBR baking for {task.asset_name}")
        return None

    def _process_uvs(self, source_file: str, task: AssetTask) -> Optional[str]:
        """UV automation processor"""
        # Placeholder for UV automation logic
        logger.info(f"UV automation for {task.asset_name}")
        return None
