# NAR Blender Asset Automation Framework - Installation Guide

Complete installation and setup instructions for the production asset pipeline.

---

## Prerequisites

- **Blender 3.0+** (4.0+ recommended)
- **Python 3.9+**
- **8GB+ RAM** (16GB recommended for batch processing)
- **GPU with CUDA support** (optional, for fast texture baking)

---

## Quick Installation (5 minutes)

### On Windows

```powershell
# 1. Clone or download the repository
cd C:\path\to\hhj

# 2. Run setup script
python setup.py develop

# 3. Verify installation
python -c "from src.blender_automation.config import BlenderAssetPipelineConfig; print('✓ Installation successful!')"
```

### On macOS/Linux

```bash
# 1. Clone or download the repository
cd /path/to/hhj

# 2. Run setup script
python3 setup.py develop

# 3. Verify installation
python3 -c "from src.blender_automation.config import BlenderAssetPipelineConfig; print('✓ Installation successful!')"
```

---

## Step-by-Step Installation

### 1. Extract Project Files

Place the project in a convenient location:
- **Windows**: `C:\Users\[YourName]\hhj` or `C:\Projects\hhj`
- **macOS/Linux**: `~/Projects/hhj` or `/opt/hhj`

### 2. Configure Blender Path

**Windows (PowerShell):**
```powershell
$env:BLENDER_PATH = "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
[Environment]::SetEnvironmentVariable("BLENDER_PATH", $env:BLENDER_PATH, "User")
```

**macOS:**
```bash
export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/blender"
echo 'export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/blender"' >> ~/.zprofile
```

**Linux:**
```bash
export BLENDER_PATH="/usr/bin/blender"
echo 'export BLENDER_PATH="/usr/bin/blender"' >> ~/.bashrc
```

### 3. Install Python Package

```bash
# Navigate to project root
cd hhj

# Install in development mode
python3 setup.py develop

# Or install for production use
python3 setup.py install
```

### 4. Verify Installation

```bash
# Test imports
python3 -c "from src.blender_automation.main import NARAssetPipeline; print('✓ Ready!')"

# List available stages
python3 -c "from src.blender_automation.config import ProcessingStage; print([s.name for s in ProcessingStage])"
```

---

## Configuration

### Create Project Config

Copy example configuration and customize:

```bash
# Windows
copy src\blender_automation\example_config.json my_project_config.json

# macOS/Linux
cp src/blender_automation/example_config.json my_project_config.json
```

Edit `my_project_config.json` with your project settings:

```json
{
  "blender_executable": "/path/to/blender",
  "quality_preset": "pc_high",
  "output_directory": "./exports",
  "asset_categories": {
    "character": {
      "target_poly_count": 100000,
      "texture_resolution": "4k"
    }
  }
}
```

---

## First Asset Processing

### Single Asset Test

```bash
# Windows
blender --background --python src/blender_automation/main.py -- `
  --mode single `
  --input "path\to\character_sculpt.blend" `
  --asset-name "test_character" `
  --asset-category character `
  --config my_project_config.json

# macOS/Linux
blender --background --python src/blender_automation/main.py -- \
  --mode single \
  --input "path/to/character_sculpt.blend" \
  --asset-name "test_character" \
  --asset-category character \
  --config my_project_config.json
```

Monitor output:
```
[INFO] Loading pipeline configuration...
[INFO] Starting asset processing: test_character
[INFO] Stage 1/5: Retopology...
[INFO] Stage 2/5: LOD Generation...
[INFO] Stage 3/5: UV Automation...
[INFO] Stage 4/5: PBR Baking...
[INFO] Stage 5/5: Export...
[INFO] ✓ Asset processing complete!
```

---

## Batch Processing Setup

### For Production Pipelines

```bash
# Process entire asset library
python3 src/blender_automation/production_workflow.py \
  --source-dir ./assets/source \
  --mode character \
  --batch-size 5 \
  --threads 4 \
  --project-root .
```

This will:
1. Discover all assets in source directory
2. Prioritize by category and name
3. Process in parallel batches
4. Generate quality report
5. Export production log

---

## Directory Structure

After installation, your project should look like:

```
hhj/
├── src/
│   └── blender_automation/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── lod_generator.py
│       ├── pbr_baker.py
│       ├── uv_automation.py
│       ├── retopology_tools.py
│       ├── batch_processor.py
│       ├── production_workflow.py
│       ├── README.md
│       ├── USAGE_EXAMPLES.md
│       ├── QUICK_START.md
│       ├── UNREAL_ENGINE_INTEGRATION.md
│       └── example_config.json
├── setup.py
├── INSTALL.md
├── assets/
│   └── source/           # Your source Blender files
├── exports/              # Output processed assets
├── configs/              # Project configurations
└── logs/                 # Processing logs
```

Create these directories if needed:

**Windows:**
```powershell
mkdir assets\source
mkdir exports
mkdir configs
mkdir logs
```

**macOS/Linux:**
```bash
mkdir -p assets/source exports configs logs
```

---

## Troubleshooting

### "Blender not found"

**Windows:**
```powershell
# Find Blender installation
where blender
# Or manually set
$env:BLENDER_PATH = "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
```

**macOS/Linux:**
```bash
# Find Blender installation
which blender
# Or set manually
export BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/blender"
```

### "Module not found" Error

```bash
# Reinstall in development mode
python3 setup.py develop

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/hhj/src"
```

### "CUDA out of memory"

Edit your config and disable GPU:
```json
{
  "pbr_settings": {
    "use_gpu": false,
    "gpu_device": "CPU"
  }
}
```

Or reduce quality:
```json
{
  "pbr_settings": {
    "bake_samples": 32,
    "default_resolution": "2k"
  }
}
```

### "Quadriflow not available"

Blender will automatically fall back to decimation method. To install Quadriflow addon:

1. Download from: https://github.com/norgeotloic/quadriflow
2. Copy to Blender addons folder
3. Enable in Blender preferences

---

## Next Steps

1. **Read Documentation:**
   - `src/blender_automation/README.md` - Overview
   - `src/blender_automation/USAGE_EXAMPLES.md` - 30+ examples
   - `src/blender_automation/QUICK_START.md` - 5-minute guide

2. **Process First Asset:**
   - Follow "First Asset Processing" section above
   - Verify output files in `exports/` directory

3. **Configure for Your Project:**
   - Customize `my_project_config.json`
   - Set quality presets for your target platform

4. **Integrate with Engine:**
   - See `UNREAL_ENGINE_INTEGRATION.md` for UE5
   - Follow material setup guide
   - Test LOD switching in viewport

5. **Scale to Production:**
   - Use `production_workflow.py` for batch processing
   - Monitor `asset_production.log`
   - Review quality reports

---

## System Requirements for Production

| Task | RAM | GPU | CPU |
|------|-----|-----|-----|
| Single Asset | 8GB | Optional | 4 cores |
| 5 Assets (parallel) | 16GB | Recommended | 8 cores |
| 20+ Assets (batch) | 32GB | Required | 16+ cores |
| Cloud Rendering | 64GB | Multiple GPUs | 32+ cores |

---

## Support and Documentation

- **Quick Start:** `src/blender_automation/QUICK_START.md`
- **Complete Examples:** `src/blender_automation/USAGE_EXAMPLES.md`
- **Unreal Integration:** `src/blender_automation/UNREAL_ENGINE_INTEGRATION.md`
- **Configuration Reference:** `src/blender_automation/README.md`

---

**Status:** Ready for production use
**Version:** 1.0.0
**Last Updated:** September 2026

