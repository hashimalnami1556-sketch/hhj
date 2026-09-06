# Unreal Engine 5 Integration Guide
## NAR Asset Pipeline → UE5 Workflow

Complete guide for integrating Blender-processed assets into Unreal Engine 5.

---

## Table of Contents
1. [Asset Export & Import](#asset-export--import)
2. [Project Setup](#project-setup)
3. [Material Configuration](#material-configuration)
4. [LOD Configuration](#lod-configuration)
5. [Character Setup](#character-setup)
6. [Environment Integration](#environment-integration)
7. [Quality Settings](#quality-settings)
8. [Performance Optimization](#performance-optimization)
9. [Workflow Automation](#workflow-automation)

---

## Asset Export & Import

### Export from Blender

The pipeline exports assets as **FBX** (recommended for Unreal):

```
export/
├── character_001/
│   ├── character_001.fbx          ← Main mesh
│   ├── lods/
│   │   ├── character_001_LOD0.fbx
│   │   ├── character_001_LOD1.fbx
│   │   ├── character_001_LOD2.fbx
│   │   └── character_001_LOD3.fbx
│   └── textures/
│       ├── character_001_Normal.exr
│       ├── character_001_Roughness.exr
│       ├── character_001_Metallic.exr
│       ├── character_001_AO.exr
│       ├── character_001_Height.exr
│       └── character_001_Emissive.exr
```

### Import Settings (Mesh)

**Skeletal Mesh (Characters):**
```
Skeletal Mesh: ✓
Use T0 as Ref Pose: ✓
Create Physics Asset: ✓
Skeletal LOD Settings:
  - Import LODs: ✓
  - LOD Settings: Skeletal
```

**Static Mesh (Props/Environment):**
```
Import as Static: ✓
Create Collision: ✓
Use Full Precision UVs: ✓
Generate Lightmap UVs: ✓
```

### Import Settings (Materials)

```
Import Materials: ✓
Import Textures: ✓
Material Import Method: Create New Materials
```

---

## Project Setup

### Directory Structure

Organize content in UE5 Content Browser:

```
Content/
├── Characters/
│   ├── Player/
│   │   └── Protagonist_NAR/
│   │       ├── Meshes/
│   │       ├── Materials/
│   │       ├── Skeletons/
│   │       └── Animations/
│   ├── NPCs/
│   └── Enemies/
├── Environments/
│   ├── SkyCity_001/
│   │   ├── Meshes/
│   │   ├── Materials/
│   │   └── Textures/
│   ├── ShatteredWastes_001/
│   └── BioluminescentDeep_001/
├── Weapons/
│   ├── Swords/
│   ├── Bows/
│   └── Spells/
├── Props/
├── VFX/
├── Audio/
└── UI/
```

### Texture Organization

After import, organize textures by type:

```
Textures/
├── Normal_Maps/
├── Roughness_Maps/
├── Metallic_Maps/
├── AO_Maps/
├── Height_Maps/
└── Emissive_Maps/
```

---

## Material Configuration

### Master Material Setup

**Create Master Material:**
1. Right-click → Material
2. Name: `M_PBR_Master`

**Material Nodes:**

```
Base Color ← Texture Sample (RGB)
Normal ← Texture Sample → Normal Map Node
Roughness ← Texture Sample (R channel)
Metallic ← Texture Sample (R channel)
Ambient Occlusion ← Texture Sample (R channel) → Multiply with Base Color
```

### Material Function Hierarchy

```
MF_PBR_Master
├── MF_NormalMapping
├── MF_Roughness
├── MF_Metallic
└── MF_AmbientOcclusion
```

### Material Instance Creation

For each asset, create Material Instance from Master:

```cpp
// In Content Browser:
Right-click Master Material → Create Material Instance
// Name: MI_[AssetName]_[Material]
// Set Textures:
// - Base Color
// - Normal Map
// - Roughness
// - Metallic
// - AO
```

### PBR Settings

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Metallic | 0.0-1.0 | Metal intensity |
| Roughness | 0.0-1.0 | Surface smoothness |
| Specular | 0.5 | Default UE5 setting |
| AO Multiply | Connected | Shadows in crevices |

---

## LOD Configuration

### LOD Setup in UE5

**For Static Meshes:**

1. **Import FBX with LODs:**
   - Unreal auto-detects LOD naming (LOD0, LOD1, etc.)
   - Mesh > LOD Settings > Number of LODs: 4

2. **Set Screen Size:**
   - LOD 0: 100% (>450px)
   - LOD 1: 50% (200-450px)
   - LOD 2: 25% (100-200px)
   - LOD 3: 10% (<100px)

**For Skeletal Meshes:**

```cpp
// Skeletal Mesh LOD Settings:
Skeletal LOD Settings:
  - Import LODs: ✓
  - Update Skeleton Reference Pose: ✓
  - Create Physics Asset: ✓
  - Skeletal LOD Settings:
    LOD 0: Full detail, high polygon
    LOD 1: 50% reduction
    LOD 2: 25% reduction
    LOD 3: Simplified silhouette
```

### LOD Screen Size Chart

```
Distance (m)  |  Screen Size (px)  |  LOD
0 - 10        |  > 450             |  0
10 - 50       |  200 - 450         |  1
50 - 200      |  100 - 200         |  2
200+          |  < 100             |  3
```

---

## Character Setup

### Skeleton Configuration

**Import Character:**
1. FBX > Skeletal Mesh: ✓
2. Skeleton: Create new or link existing
3. Import Morph Targets: ✓ (if rigged)

**Set up in Character Blueprint:**

```cpp
class ANARCharacter : ACharacter
{
public:
    ANARCharacter();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

protected:
    // Skeletal mesh component
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class USkeletalMeshComponent* SkeletalMesh;

    // Set LOD bias
    UPROPERTY(EditAnywhere)
    float LODBias = 0.0f;

    void SetupMesh();
};
```

### Animation Blueprint Setup

```
AnimBP_NAR_Character
├── State Machine
│   ├── Idle
│   │   └── Idle_Montage
│   ├── Running
│   │   └── Run_Montage
│   ├── Combat
│   │   ├── Attack_Light
│   │   ├── Attack_Heavy
│   │   └── Dodge
│   └── Traversal
│       ├── Climb
│       ├── Glide
│       └── WallRun
└── Blend Spaces
    ├── BS_Locomotion (Speed)
    └── BS_AimOffset (Aim angle)
```

---

## Environment Integration

### Large-Scale Environment

**Setup for open world:**

```cpp
// Level Blueprint
void ALevel::SetupEnvironment()
{
    // Streaming levels
    LoadStreamingLevel("SkyCity_Sector_01");
    LoadStreamingLevel("ShatteredWastes_Sector_01");
    
    // LOD system
    SetupLODSystem();
    
    // Lighting
    SetupDynamicLighting();
    
    // Culling
    SetupOcclusionCulling();
}
```

### Material Layering

For large environments, use Master Material with many variations:

```
M_Environment_Master
├── Layer: Grass
├── Layer: Rock
├── Layer: Dirt
├── Layer: Vegetation
└── Layer: Structures
```

### Texture Streaming

Enable virtual texture streaming in project settings:

```
Project Settings > Engine > Rendering > Textures
├── Enable Virtual Texture Streaming: ✓
├── Max Virtual Texture Size: 16384
├── Virtual Texture Tile Size: 128
└── Pool Size: 256
```

---

## Quality Settings

### Scalability Settings

Create quality presets in `DefaultScalability.ini`:

```ini
[ScalabilityGroups]
sg.ResolutionQuality=100
sg.ViewDistanceQuality=3
sg.AntiAliasingQuality=3
sg.ShadowQuality=3
sg.GlobalIlluminationQuality=3
sg.ReflectionQuality=3
sg.TextureQuality=3
sg.EffectsQuality=3
sg.FoliageQuality=3
sg.ShadingQuality=3

[Epic]
sg.TextureQuality=4
sg.EffectsQuality=4
sg.ViewDistanceQuality=4

[High]
sg.TextureQuality=3
sg.EffectsQuality=3
sg.ViewDistanceQuality=3

[Medium]
sg.TextureQuality=2
sg.EffectsQuality=2
sg.ViewDistanceQuality=2

[Low]
sg.TextureQuality=1
sg.EffectsQuality=1
sg.ViewDistanceQuality=1
```

### LOD Distance Settings

```cpp
// DefaultEngine.ini
[/Script/Engine.Engine]
gMinSkelMeshVerts=12000
gMaxSkelMeshVerts=65000

[/Script/Engine.StaticMeshComponent]
StreamingDistanceMultiplier=1.0
```

---

## Performance Optimization

### Memory Management

**Measure asset memory:**
```cpp
// Console:
stat unit     // Frame time
stat detailed // Detailed stats
stat memory   // Memory usage
```

**Optimize:**
1. Reduce texture resolution for distant assets
2. Use texture atlasing where possible
3. Pool frequently instantiated assets
4. Unload unused levels

### Draw Call Optimization

**Combine materials:** Use fewer material instances

**Instance rendering:**
```cpp
// Use Hierarchical Instance Static Mesh Component
HISM = NewObject<UHierarchicalInstancedStaticMeshComponent>();
HISM->AddInstance(Transform);
```

### Culling Strategy

```cpp
// Enable all culling methods
GetWorld()->GetFirstPlayerController()->GetPawn()
    ->GetRootComponent()
    ->bVisualizeComponent = true;

// Occlusion culling
Level->GetWorldSettings()->bEnableWorldComposition = true;
Level->GetWorldSettings()->bUseClientSideLevelStreaming = true;
```

---

## Workflow Automation

### Blueprint Automation

Create asset import script:

```cpp
// Content Browser Callback
void FAssetImportCallback::OnAssetImported(UObject* ImportedAsset)
{
    if (USkeletalMesh* Mesh = Cast<USkeletalMesh>(ImportedAsset))
    {
        // Auto-setup materials
        SetupCharacterMaterials(Mesh);
        
        // Configure LODs
        ConfigureLODs(Mesh);
        
        // Setup physics
        CreatePhysicsAsset(Mesh);
    }
    
    if (UStaticMesh* Mesh = Cast<UStaticMesh>(ImportedAsset))
    {
        // Setup environment
        ConfigureEnvironmentMesh(Mesh);
        
        // Enable collision
        GenerateCollision(Mesh);
    }
}
```

### Python Automation Script

```python
# uasset_automation.py
import unreal

@unreal.ufunction(unreal.FunctionFlags.EDITOR_ONLY)
def import_and_setup_asset(asset_path, asset_type):
    """Import asset and auto-configure for game"""
    
    # Import
    imported_asset = unreal.EditorAssetLibrary.duplicate_asset(
        asset_path, 
        f"/Game/Assets/{asset_type}"
    )
    
    # Setup based on type
    if asset_type == "Character":
        setup_character(imported_asset)
    elif asset_type == "Environment":
        setup_environment(imported_asset)
    elif asset_type == "Weapon":
        setup_weapon(imported_asset)
    
    return imported_asset

def setup_character(mesh):
    """Configure character mesh"""
    mesh.set_editor_property('enable_skeletal_instancing', True)
    mesh.set_editor_property('use_full_precision_uvs', True)
    # ... more settings

# Usage
unreal.log("Importing assets...")
for asset_file in asset_files:
    unreal.execute_console_command(
        f"Python code=import_and_setup_asset('{asset_file}', 'Character')"
    )
unreal.log("✓ Assets imported and configured!")
```

---

## Real-Time Viewport Shading

### Material Preview

In Unreal Editor viewport:
1. Viewport > Lit (shows realistic materials)
2. Show > Material Diffuse (base color)
3. Show > Normal Map (surface detail)
4. Show > Wireframe (polygon structure)

### Shader Complexity Visualization

```
Viewport > Visualize > Shader Complexity
```

Shows:
- Green: Simple (1-5 instructions)
- Yellow: Moderate (5-15 instructions)
- Red: Complex (>15 instructions)

---

## Troubleshooting

### Common Import Issues

#### Mesh appears dark/black
```
Solution:
1. Check normal maps are imported correctly
2. Disable "Negate Green Channel" if needed
3. Check material connections
```

#### LODs not showing
```
Solution:
1. Verify LOD naming: _LOD0, _LOD1, etc.
2. Check "Import LODs" is enabled
3. Adjust screen size thresholds
```

#### Materials not applying
```
Solution:
1. Reimport with "Import Materials" ✓
2. Check material slots match
3. Reapply materials in editor
```

#### UV seams visible
```
Solution:
1. Increase texture resolution (2K → 4K)
2. Adjust island margin in Blender
3. Use seamless texture authoring techniques
```

---

## Production Checklist

- [ ] Assets exported from Blender pipeline
- [ ] FBX files organized by type
- [ ] Textures organized by map type
- [ ] Materials created from master material
- [ ] LOD distances configured
- [ ] Characters rigged and skeletal mesh setup
- [ ] Physics assets created
- [ ] Collision meshes generated
- [ ] Material instances assigned to meshes
- [ ] LODs validated in viewport
- [ ] Performance metrics within budget
- [ ] Memory usage optimized
- [ ] Draw calls minimized
- [ ] Level streaming configured
- [ ] Occlusion culling baked
- [ ] Quality settings tested on target hardware

---

## Performance Targets

| Target | Character | Environment | Prop |
|--------|-----------|------------|------|
| Triangle Count | 150k | 500k | 50k |
| Texture Memory | 256MB | 1GB | 64MB |
| Draw Calls | 5-10 | 20-50 | 2-3 |
| Frame Time (60fps) | 8-16ms | 10-16ms | 2-4ms |

---

## References

- [Unreal Engine 5 Documentation](https://docs.unrealengine.com)
- [Asset Importing Guide](https://docs.unrealengine.com/5.0/en-US/importing-fbx-content-into-unreal-engine/)
- [Material System](https://docs.unrealengine.com/5.0/en-US/materials-in-unreal-engine/)
- [LOD System](https://docs.unrealengine.com/5.0/en-US/using-lods-in-unreal-engine/)
- [Performance Optimization](https://docs.unrealengine.com/5.0/en-US/performance-optimization-in-unreal-engine/)

---

**Last Updated: September 6, 2026**  
**For: NAR Chronicles - Unreal Engine 5**
