# Quick Start Guide - Asset Production Pipeline
## 5 Minutes to First Asset

Get up and running with the NAR asset production pipeline in under 5 minutes.

---

## 📋 Prerequisites

- Blender 3.0+ installed
- Python 3.9+
- 8GB+ RAM
- Sample assets (or use test data)

---

## 🚀 Installation (2 min)

### 1. Copy Pipeline to Your Project

```bash
# Navigate to your game project
cd /path/to/game/project

# Copy the blender_automation folder
cp -r src/blender_automation ./
```

### 2. Verify Installation

```bash
# Test that pipeline imports correctly
python3 -c "from blender_automation.config import BlenderAssetPipelineConfig; print('✓ Pipeline installed successfully')"
```

---

## 🎯 Process Your First Asset (3 min)

### Option 1: Command Line (Easiest)

```bash
# Process a single character asset
blender --background --python src/blender_automation/main.py -- \
  --mode single \
  --input path/to/character_sculpt.blend \
  --asset-name "my_character" \
  --asset-category character
```

**What happens:**
1. Retopology (high-poly → low-poly)
2. LOD generation (4 quality tiers)
3. UV unwrapping (UDIM layout)
4. PBR baking (6 texture maps)
5. Export (ready for game engine)

### Option 2: Python Script

Create `process_asset.py`:

```python
from blender_automation.main import NARAssetPipeline

pipeline = NARAssetPipeline()

success = pipeline.process_single_asset(
    source_file="character_sculpt.blend",
    asset_name="protagonist",
    asset_category="character"
)

print("✓ Done!" if success else "✗ Failed")
```

Run it:
```bash
python3 process_asset.py
```

### Option 3: Production Workflow

Process multiple assets with automatic prioritization:

```bash
python3 src/blender_automation/production_workflow.py \
  --source-dir ./assets/source \
  --mode character \
  --batch-size 5 \
  --threads 4
```

---

## 📂 Expected Output

After processing, you'll find:

```
export/my_character/
├── my_character.fbx                    ← Main mesh
├── lods/
│   ├── my_character_LOD0.fbx          ← High detail
│   ├── my_character_LOD1.fbx          ← Medium
│   ├── my_character_LOD2.fbx          ← Low
│   └── my_character_LOD3.fbx          ← Very low
└── textures/
    ├── my_character_Normal.exr         ← Surface detail
    ├── my_character_Roughness.exr      ← Shininess
    ├── my_character_Metallic.exr       ← Metal areas
    ├── my_character_AO.exr             ← Shadows
    ├── my_character_Height.exr         ← Displacement
    └── my_character_Emissive.exr       ← Self-light
```

---

## 🎮 Import into Unreal Engine 5

### 1. Create Content Folder

In UE5 Content Browser:
```
Content/
└── Characters/
    └── my_character/
        ├── Meshes/
        ├── Materials/
        └── Textures/
```

### 2. Import Mesh

**File > Import**
- Source: `my_character.fbx`
- Skeletal Mesh: ✓
- Import LODs: ✓
- Import Materials: ✓
- Import Textures: ✓

### 3. Import Textures

**Drag & drop** texture files into Textures folder:
- `my_character_Normal.exr` → Texture > Compression: Mask (DXT5, BC5)
- `my_character_Roughness.exr` → Texture > Compression: Roughness
- `my_character_Metallic.exr` → Texture > Compression: Metallic
- `my_character_AO.exr` → Texture > Compression: Default (sRGB off)

### 4. Create Material

**Right-click > Material > M_Character_Master**

Material graph:
```
Base Color ← Normal texture
Normal ← Normal map node ← Normal texture
Roughness ← Roughness texture
Metallic ← Metallic texture
Ambient Occlusion ← AO texture (multiply with Base Color)
```

### 5. Create Material Instance

**Right-click M_Character_Master > Create Material Instance**

Assign textures in the instance.

### 6. Assign to Mesh

1. Open skeletal mesh
2. Material Slots > Set Material 0 to your instance
3. Save and compile

---

## ⚙️ Configuration

### Customize for Your Project

Edit `example_config.json`:

```json
{
  "quality_presets": {
    "pc_high": {
      "target_poly_count": 500000,
      "texture_resolution": "4k",
      "bake_samples": 256
    }
  },
  "lod_settings": {
    "reduction_ratios": [1.0, 0.5, 0.25, 0.1]
  }
}
```

Then use it:

```bash
blender --background --python main.py -- \
  --config example_config.json \
  --mode single \
  --input asset.blend \
  --asset-name "asset"
```

---

## 🐛 Troubleshooting

### "Blender not found"
```bash
# Make sure Blender is in your PATH
which blender

# If not, provide full path
/Applications/Blender.app/Contents/MacOS/blender \
  --background --python main.py -- --mode info
```

### "CUDA out of memory"
```bash
# Use CPU or reduce quality
blender --python main.py -- \
  --mode single \
  --input asset.blend \
  --asset-name "asset"
# Edit config: "use_gpu": false
```

### "Quadriflow not available"
```bash
# Use decimate fallback (automatic)
# Or install Quadriflow addon in Blender
```

### Asset looks black in Unreal
```
Unreal Engine > Material:
1. Check normal map is imported as "Normal Map"
2. Uncheck "Flip Green Channel"
3. Verify texture compression settings
```

---

## 📊 Performance Tips

### For Fast Processing
```bash
# Reduce samples for faster baking
python3 -c "
config = __import__('blender_automation.config', fromlist=['BlenderAssetPipelineConfig']).BlenderAssetPipelineConfig()
config.pbr_settings.bake_samples = 32
config.pbr_settings.default_resolution = '2k'
"
```

### For High Quality
```bash
# Increase samples for better quality
# Edit config: bake_samples = 512, resolution = 8k
```

### For Batch Processing
```bash
# Process multiple assets in parallel
python3 production_workflow.py \
  --source-dir ./assets/source \
  --threads 8  # Use all cores
```

---

## 🔗 Next Steps

1. **Process more assets**: Try different categories (weapon, prop, environment)
2. **Batch processing**: Use `production_workflow.py` for multiple assets
3. **Customize quality**: Edit configuration for your needs
4. **Integrate with game engine**: Follow [UNREAL_ENGINE_INTEGRATION.md](UNREAL_ENGINE_INTEGRATION.md)
5. **Automate workflow**: Set up CI/CD pipeline for asset production

---

## 📚 Documentation

- **[README.md](README.md)** - Complete feature overview
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - 30+ examples
- **[UNREAL_ENGINE_INTEGRATION.md](UNREAL_ENGINE_INTEGRATION.md)** - UE5 setup
- **[config.py](config.py)** - Configuration reference
- **[production_workflow.py](production_workflow.py)** - Real-world workflow

---

## ✅ Checklist

- [ ] Blender 3.0+ installed
- [ ] Pipeline copied to project
- [ ] Sample asset ready
- [ ] First asset processed
- [ ] Output files verified
- [ ] Imported into Unreal Engine
- [ ] Material created and assigned
- [ ] Asset visible in viewport
- [ ] Performance acceptable
- [ ] Ready to scale up

---

## 🚀 You're Ready!

Congratulations! You've successfully:
1. ✓ Set up the pipeline
2. ✓ Processed your first asset
3. ✓ Imported into game engine
4. ✓ Created materials

**Next: Scale up to production!**

```bash
# Process entire asset library
python3 production_workflow.py \
  --source-dir ./assets/source \
  --threads 8
```

---

**Questions?** Check the [README.md](README.md) for comprehensive documentation.

**Ready to ship?** Review the [UNREAL_ENGINE_INTEGRATION.md](UNREAL_ENGINE_INTEGRATION.md) for production best practices.

---

*NAR Chronicles Asset Pipeline - Quick Start*  
*Updated: September 6, 2026*
