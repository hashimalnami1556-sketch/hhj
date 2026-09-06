# Blender Asset Automation - Usage Examples

Complete examples for common asset production workflows.

---

## Table of Contents
1. [Command Line Usage](#command-line-usage)
2. [Python API Usage](#python-api-usage)
3. [Character Pipeline](#character-pipeline)
4. [Environment Pipeline](#environment-pipeline)
5. [Prop Pipeline](#prop-pipeline)
6. [Batch Production](#batch-production)
7. [Advanced Configuration](#advanced-configuration)

---

## Command Line Usage

### Example 1: Process a Single Character

```bash
blender --background --python main.py -- \
  --mode single \
  --input character_sculpt.blend \
  --asset-name "protagonist_naris" \
  --asset-category character \
  --stages retopo lod uv pbr export
```

**What happens:**
1. ✓ Retopologize high-poly sculpt to 100k polygons
2. ✓ Generate 4 LOD levels (100%, 50%, 25%, 10%)
3. ✓ Create 2 UV sets (color + lightmap)
4. ✓ Bake 6 texture maps (4K resolution)
5. ✓ Export as FBX + textures

**Output:**
```
export/protagonist_naris/
├── protagonist_naris.fbx
├── lods/
│   ├── protagonist_naris_LOD0.fbx
│   ├── protagonist_naris_LOD1.fbx
│   ├── protagonist_naris_LOD2.fbx
│   └── protagonist_naris_LOD3.fbx
└── textures/
    ├── protagonist_naris_Normal.exr
    ├── protagonist_naris_Roughness.exr
    ├── protagonist_naris_Metallic.exr
    ├── protagonist_naris_AO.exr
    ├── protagonist_naris_Height.exr
    └── protagonist_naris_Emissive.exr
```

### Example 2: Batch Process Environment Assets

```bash
blender --background --python main.py -- \
  --mode batch \
  --input ./assets/source/environments/ \
  --asset-category environment \
  --threads 8 \
  --output ./assets/export/
```

**Input Directory Structure:**
```
./assets/source/environments/
├── tree_oak_01.blend
├── tree_birch_01.blend
├── rock_formation_01.blend
├── grass_field_01.blend
└── water_pool_01.blend
```

**Output:**
```
./assets/export/
├── tree_oak_01/
│   ├── tree_oak_01.fbx
│   ├── lods/
│   └── textures/
├── tree_birch_01/
│   └── ...
└── processing_report.json
```

### Example 3: Only Generate LODs (Skip Retopo)

```bash
blender --background --python main.py -- \
  --mode single \
  --input lowpoly_mesh.fbx \
  --asset-name "tree_final" \
  --stages lod uv pbr export
```

**Use case:** When you already have a properly retopologized mesh

### Example 4: Only Bake Textures (Skip LODs)

```bash
blender --background --python main.py -- \
  --mode single \
  --input mesh_with_uvs.fbx \
  --asset-name "sword_weapon" \
  --asset-category weapon \
  --stages pbr export
```

**Use case:** Quick iteration on textures for already-optimized meshes

### Example 5: View Configuration

```bash
blender --background --python main.py -- --mode info
```

**Output:**
```
============================================================
NAR ASSET PIPELINE CONFIGURATION
============================================================

project_root: /home/user/hhj

directories:
  assets: /home/user/hhj/assets
  blender: /home/user/hhj/assets/blender
  source: /home/user/hhj/assets/blender/source
  work: /home/user/hhj/assets/blender/work
  export: /home/user/hhj/assets/blender/export
  textures: /home/user/hhj/assets/blender/textures

quality_preset: pc_high

============================================================
```

---

## Python API Usage

### Example 1: Basic Asset Processing

```python
from blender_automation.main import NARAssetPipeline

# Initialize pipeline
pipeline = NARAssetPipeline()

# Process a single asset
success = pipeline.process_single_asset(
    source_file="character_highpoly.blend",
    asset_name="npc_guard",
    asset_category="character",
    stages=['retopo', 'lod', 'uv', 'pbr', 'export']
)

if success:
    print("✓ Asset processed successfully!")
else:
    print("✗ Processing failed")
```

### Example 2: Custom Configuration

```python
from blender_automation.config import BlenderAssetPipelineConfig
from blender_automation.main import NARAssetPipeline

# Create custom config
config = BlenderAssetPipelineConfig("/my/project/path")

# Customize LOD settings
config.lod_settings.reduction_ratios = (1.0, 0.4, 0.2, 0.05)
config.lod_settings.lod_levels = 4

# Use high-quality baking
config.pbr_settings.bake_samples = 512
config.pbr_settings.default_resolution = "8k"
config.pbr_settings.use_gpu = True

# Create pipeline with custom config
pipeline = NARAssetPipeline()
pipeline.config = config

# Process asset
pipeline.process_single_asset(
    source_file="highpoly_model.blend",
    asset_name="detailed_prop",
    asset_category="prop"
)
```

### Example 3: Direct Module Usage

```python
import bpy
from blender_automation.retopology_tools import AutoRetopologyPipeline
from blender_automation.lod_generator import AutoLODPipeline
from blender_automation.uv_automation import AutoUVPipeline
from blender_automation.pbr_baker import HighPolyBakerPipeline
from blender_automation.config import BlenderAssetPipelineConfig

# Setup
config = BlenderAssetPipelineConfig()

# Load mesh in Blender
bpy.ops.import_scene.fbx(filepath="source_mesh.fbx")
highpoly_obj = bpy.context.selected_objects[0]

# Step 1: Retopology
print("Step 1: Retopology...")
retopo_pipeline = AutoRetopologyPipeline(config)
lowpoly_obj = retopo_pipeline.process_asset(highpoly_obj, "character", "quadriflow")

# Step 2: LOD Generation
print("Step 2: LOD Generation...")
lod_pipeline = AutoLODPipeline(config)
lod_meshes = lod_pipeline.generator.generate_lods(lowpoly_obj)

# Step 3: UV Automation
print("Step 3: UV Automation...")
uv_pipeline = AutoUVPipeline(config)
uv_pipeline.process_asset(lowpoly_obj, generate_lightmap=True)

# Step 4: PBR Baking
print("Step 4: PBR Baking...")
baker = HighPolyBakerPipeline(config)
baker.baker.setup_baking_scene(lowpoly_obj, highpoly_obj)
baked_textures = baker.baker.bake_textures()

print("✓ All stages completed!")
```

---

## Character Pipeline

### Complete Character Workflow

```python
from blender_automation.main import NARAssetPipeline

pipeline = NARAssetPipeline()

# Customize for characters
pipeline.config.retopology_settings.character_target_poly_count = 100000
pipeline.config.pbr_settings.bake_samples = 256
pipeline.config.uv_settings.generate_lightmap_uvs = True

# Process multiple characters
characters = [
    ("protagonist_sculpt.blend", "protagonist_naris"),
    ("guard_sculpt.blend", "npc_guard_001"),
    ("merchant_sculpt.blend", "npc_merchant"),
    ("dragon_sculpt.blend", "boss_dragon"),
]

for source_file, asset_name in characters:
    print(f"Processing {asset_name}...")
    success = pipeline.process_single_asset(
        source_file=source_file,
        asset_name=asset_name,
        asset_category="character"
    )
    print(f"  {'✓' if success else '✗'} Complete")
```

### Character with Rigging Preparation

```python
import bpy
from blender_automation.retopology_tools import AutoRetopologyPipeline
from blender_automation.config import BlenderAssetPipelineConfig

config = BlenderAssetPipelineConfig()
config.retopology_settings.use_mesh_symmetry = True  # Important for rigging!

# Import and retopologize
bpy.ops.import_scene.fbx(filepath="character_sculpt.fbx")
highpoly = bpy.context.selected_objects[0]

retopo = AutoRetopologyPipeline(config)
lowpoly = retopo.process_asset(
    source_obj=highpoly,
    asset_category="character",
    method="quadriflow"
)

# Export ready for rigging
bpy.context.view_layer.objects.active = lowpoly
bpy.ops.export_scene.fbx(filepath="character_ready_for_rigging.fbx")
```

---

## Environment Pipeline

### Large-Scale Environment

```bash
# Process all environment assets with 8 threads
blender --background --python main.py -- \
  --mode batch \
  --input ./environments/source/ \
  --asset-category environment \
  --threads 8 \
  --output ./environments/export/
```

### Custom Environment Quality

```python
from blender_automation.config import BlenderAssetPipelineConfig
from blender_automation.main import NARAssetPipeline

config = BlenderAssetPipelineConfig()

# Optimize for vast open world
config.lod_settings.reduction_ratios = (1.0, 0.4, 0.15, 0.05)
config.pbr_settings.default_resolution = "4k"
config.batch_settings.num_threads = 16  # Use many threads

pipeline = NARAssetPipeline()
pipeline.config = config

report = pipeline.process_batch(
    source_directory="./assets/environments/",
    asset_category="environment",
    num_threads=16
)

print(f"Processed {report['summary']['completed']} environments")
print(f"Success rate: {report['summary']['success_rate']:.1f}%")
```

### Vegetation Batch Processing

```python
from pathlib import Path
from blender_automation.batch_processor import BatchProcessor, AssetTask, ProcessingStatus
from blender_automation.config import BlenderAssetPipelineConfig

config = BlenderAssetPipelineConfig()
processor = BatchProcessor(config, num_threads=8)

# Add vegetation assets with priority
vegetation_types = [
    ("trees", 1),      # High priority
    ("shrubs", 2),     # Medium priority
    ("grass", 3),      # Lower priority
]

asset_counter = 0
for veg_type, priority in vegetation_types:
    for file in Path(f"./assets/{veg_type}").glob("*.blend"):
        task = AssetTask(
            asset_id=f"veg_{asset_counter:04d}",
            asset_name=file.stem,
            source_file=str(file),
            asset_category="environment",
            priority=priority
        )
        processor.add_task(task)
        asset_counter += 1

print(f"Queued {asset_counter} vegetation assets")
```

---

## Prop Pipeline

### Quick Prop Processing

```bash
# Fast processing for small props
blender --background --python main.py -- \
  --mode single \
  --input chair_model.blend \
  --asset-name "chair_wooden_01" \
  --asset-category prop \
  --stages retopo lod uv pbr export
```

### Prop with Custom Resolution

```python
from blender_automation.config import BlenderAssetPipelineConfig
from blender_automation.main import NARAssetPipeline

config = BlenderAssetPipelineConfig()

# Props use lower resolution
config.pbr_settings.default_resolution = "2k"  # Not 4K
config.retopology_settings.target_poly_count = 30000  # Small!

pipeline = NARAssetPipeline()
pipeline.config = config

# Process collection of props
props = [
    "sword.blend",
    "shield.blend",
    "torch.blend",
    "barrel.blend",
    "crate.blend",
]

for prop_file in props:
    pipeline.process_single_asset(
        source_file=f"./props/{prop_file}",
        asset_name=prop_file.replace(".blend", ""),
        asset_category="prop"
    )
```

---

## Batch Production

### Full Asset Production Run

```bash
#!/bin/bash
# production_pipeline.sh

echo "NAR Asset Production Pipeline"
echo "=============================="

PROJECT_DIR="./assets"

# Process characters
echo "Processing characters..."
blender --background --python src/blender_automation/main.py -- \
  --mode batch \
  --input "$PROJECT_DIR/source/characters/" \
  --asset-category character \
  --threads 4

# Process environments
echo "Processing environments..."
blender --background --python src/blender_automation/main.py -- \
  --mode batch \
  --input "$PROJECT_DIR/source/environments/" \
  --asset-category environment \
  --threads 8

# Process props
echo "Processing props..."
blender --background --python src/blender_automation/main.py -- \
  --mode batch \
  --input "$PROJECT_DIR/source/props/" \
  --asset-category prop \
  --threads 4

# Process weapons
echo "Processing weapons..."
blender --background --python src/blender_automation/main.py -- \
  --mode batch \
  --input "$PROJECT_DIR/source/weapons/" \
  --asset-category weapon \
  --threads 4

echo "=============================="
echo "✓ Production pipeline completed"
```

### Production with Reporting

```python
from blender_automation.main import NARAssetPipeline
import json
from datetime import datetime

pipeline = NARAssetPipeline()

# Comprehensive production run
asset_categories = {
    "character": 50,
    "environment": 200,
    "prop": 100,
    "weapon": 30,
}

production_report = {
    "timestamp": datetime.now().isoformat(),
    "categories": {}
}

for category, estimated_count in asset_categories.items():
    print(f"\nProcessing {category} assets ({estimated_count} estimated)...")

    report = pipeline.process_batch(
        source_directory=f"./assets/source/{category}/",
        asset_category=category,
        num_threads=8
    )

    production_report["categories"][category] = report

    print(f"  Completed: {report['summary']['completed']}")
    print(f"  Failed: {report['summary']['failed']}")
    print(f"  Success: {report['summary']['success_rate']:.1f}%")

# Save comprehensive report
with open("production_report.json", "w") as f:
    json.dump(production_report, f, indent=2)

print("\n✓ Production complete - report saved to production_report.json")
```

---

## Advanced Configuration

### Multi-Platform Export

```python
from blender_automation.config import BlenderAssetPipelineConfig
from blender_automation.main import NARAssetPipeline

config = BlenderAssetPipelineConfig()

# Configure for multiple platforms
platforms = {
    "unreal": {
        "lod_levels": 4,
        "texture_resolution": "4k",
        "export_format": "fbx"
    },
    "unity": {
        "lod_levels": 3,
        "texture_resolution": "2k",
        "export_format": "glb"
    },
    "mobile": {
        "lod_levels": 2,
        "texture_resolution": "1k",
        "export_format": "glb"
    }
}

# Process for each platform
for platform, settings in platforms.items():
    print(f"Processing for {platform}...")

    config.lod_settings.lod_levels = settings["lod_levels"]
    config.pbr_settings.default_resolution = settings["texture_resolution"]

    pipeline = NARAssetPipeline()
    pipeline.config = config

    pipeline.process_single_asset(
        source_file="base_character.blend",
        asset_name=f"character_{platform}",
        asset_category="character"
    )

    print(f"  ✓ {platform} export complete")
```

### GPU vs CPU Processing

```python
from blender_automation.config import BlenderAssetPipelineConfig
from blender_automation.main import NARAssetPipeline

# High-quality with GPU
config_gpu = BlenderAssetPipelineConfig()
config_gpu.pbr_settings.use_gpu = True
config_gpu.pbr_settings.bake_samples = 256

pipeline_gpu = NARAssetPipeline()
pipeline_gpu.config = config_gpu

# Fast with CPU fallback
config_cpu = BlenderAssetPipelineConfig()
config_cpu.pbr_settings.use_gpu = False
config_cpu.pbr_settings.bake_samples = 64

pipeline_cpu = NARAssetPipeline()
pipeline_cpu.config = config_cpu

# Use GPU for hero assets, CPU for generic props
print("Processing hero character with GPU...")
pipeline_gpu.process_single_asset("protagonist.blend", "protagonist", "character")

print("Processing generic props with CPU...")
for prop in ["crate", "barrel", "table"]:
    pipeline_cpu.process_single_asset(f"{prop}.blend", prop, "prop")
```

### Custom Validation and QA

```python
from blender_automation.retopology_tools import RetopologyTools
from blender_automation.config import BlenderAssetPipelineConfig

config = BlenderAssetPipelineConfig()
tools = RetopologyTools(config)

# Import and validate asset
import bpy
bpy.ops.import_scene.fbx(filepath="exported_asset.fbx")
mesh = bpy.context.selected_objects[0]

# Run validation
validation = tools.validate_retopo_mesh(mesh)

print("\nValidation Results:")
print(f"  Manifold: {'✓' if validation['is_manifold'] else '✗'}")
print(f"  No Degenerate Faces: {'✓' if validation['no_degenerate_faces'] else '✗'}")
print(f"  Poly Count OK: {'✓' if validation['poly_count_acceptable'] else '✗'}")
print(f"  Has UVs: {'✓' if validation['has_uvs'] else '✗'}")

if not validation['valid_for_export']:
    print("\n✗ Asset failed validation!")
    print("Run cleanup_mesh() to fix issues")
    tools.cleanup_mesh(mesh)
```

---

## Performance Tips

### For Large Batches

```bash
# Use all available cores
blender --python main.py -- --threads $(nproc)

# Or specifically for 32-core machine
blender --python main.py -- --threads 32
```

### For High Quality

```python
# Increase bake samples for cinematics
config.pbr_settings.bake_samples = 512
config.pbr_settings.bake_engine = "CYCLES"
config.pbr_settings.default_resolution = "8k"
```

### For Quick Iteration

```python
# Reduce quality for fast testing
config.pbr_settings.bake_samples = 16
config.pbr_settings.use_gpu = False  # CPU can be faster for small scenes
config.pbr_settings.default_resolution = "2k"
```

---

## Troubleshooting

### "Out of Memory" Error

```python
# Reduce batch size
config.batch_settings.batch_size = 2

# Or reduce texture resolution
config.pbr_settings.default_resolution = "2k"

# Or reduce bake samples
config.pbr_settings.bake_samples = 32
```

### "Quadriflow Failed"

```python
# Use fallback method
pipeline = NARAssetPipeline()
pipeline.retopo_pipeline.process_asset(
    source_obj,
    asset_category="environment",
    method="decimate"  # Fallback to faster method
)
```

### "Processing Too Slow"

```python
# Check if GPU is being used
config.pbr_settings.use_gpu = True
config.pbr_settings.bake_engine = "CYCLES"

# Or increase threads
config.batch_settings.num_threads = 16
```

---

**Last Updated: 2026-09-06**
