# مكتبة أصول NARIS - الفهرس الشامل

**آخر تحديث:** September 2026  
**الإصدار:** v2.0 - المكتبة الموسعة  
**الحالة:** ✅ جاهز للمحركات

---

## 📋 نظرة عامة

مكتبة أصول شاملة لمشروع لعبة NARIS: Call of Naris. تتضمن:
- 🎭 **4 نماذج شخصيات** مع نسختين (بسيطة + متقدمة)
- 🛗 **14 أصل بيئة** (أرضيات، أشجار، صخور)
- ⚔️ **2 أسلحة أسطورية** مع إحصائيات وترقيات
- 🛡️ **معدات ودروع** متعددة الأنواع
- ✨ **9 تأثيرات بصرية متقدمة** (جزيئات، توهجات، موجات صدمة)
- 🎮 **11 عنصر واجهة مستخدم** (HUD, menus, inventory)

**إجمالي الأصول:** 50+ ملف مواصفات JSON + 8 برامج نصية Python

---

## 🎮 الشخصيات (Characters)

### 1. نارس - البطل الرئيسي | Naris Hero
```
📁 assets/characters/naris_hero.json
📊 النوع: Protagonist (Playable Character)
⚡ الإحصائيات: HP 100 | Poise 40 | Damage 15
🎨 المواد: ash_black, ancient_gold, naris_fire
🦴 العظام: 16 عظمة مع هيكل عظمي كامل
🎬 الرسوم المتحركة: 8 حركات أساسية
📦 النموذج:
   - naris_hero.glb (بسيط: 2.6 KB)
   - naris_hero_advanced.glb (متقدم: 4.2 KB)
```

**الميزات الخاصة:**
- سيف القصيدة (Sword of Poem) - أسطوري
- نقاط تثبيت للمعدات والأسلحة
- نظام متغيرات الأثير (Aether variations)
- تأثيرات بصرية تلقائية

---

### 2. الذئب الروحاني | Spirit Wolf
```
📁 assets/characters/spirit_wolf.json
📊 النوع: Companion (رفيق اللعبة)
⚡ الإحصائيات: HP 60 | Bond 0-100 | Damage 10
🎨 المواد: mist_cyan, aether_violet, naris_fire
🎬 الرسوم المتحركة: 8 حركات + تأثيرات روح
📦 النموذج:
   - spirit_wolf.glb (بسيط: 2.6 KB)
   - spirit_wolf_advanced.glb (متقدم: 4.1 KB)
```

**الميزات الخاصة:**
- الشفافية: 0.7 (نصف شفاف)
- إضاءة الحافة السماوية (Cyan rim light)
- نقاط تثبيت للجزيئات على العمود الفقري والعيون
- نظام الرابط الروحي (Echo Link)

---

### 3. وحش العظام | Bone Beast
```
📁 assets/characters/bone_beast.json
📊 النوع: Enemy (عدو مبكر)
⚡ الإحصائيات: HP 45 | Poise 30 | Damage 8
🎨 المواد: ash_black, aether_violet
🎬 الرسوم المتحركة: 6 حركات + رد الفعل
📦 النموذج:
   - bone_beast.glb (بسيط: 2.6 KB)
   - bone_beast_advanced.glb (متقدم: 4.0 KB)
```

**نظام المقاومة:**
- النار: 0.8x (ضعيف ضد النار)
- الأثير: 1.2x (قوي ضد الأثير)
- الفراغ: 0.9x (عادي ضد الفراغ)

---

### 4. عملاق الرماد | Ash Giant
```
📁 assets/characters/ash_giant.json
📊 النوع: Boss (زعيم مرحلة الفتح)
⚡ الإحصائيات: HP 200 | Poise 80 | Damage 25
🎨 المواد: ash_black, naris_fire, aether_violet, ancient_gold
🎬 الرسوم المتحركة: تحول ديناميكي بين المراحل
📦 النموذج:
   - ash_giant.glb (بسيط: 1.1 KB)
   - ash_giant_advanced.glb (متقدم: 4.3 KB)
```

**نظام المراحل:**
- **المرحلة 1** (HP 100-200): مختوم، حركات بطيئة، توهج أثير
- **المرحلة 2** (HP 50-100): مستيقظ، شقوق نار، حركات أسرع
- **المرحلة 3** (HP 0-50): الشكل النهائي، جميع المواد تتوهج، هجمات ضخمة

**القدرات:**
1. `slam_attack` - ضربة أرضية قوية
2. `fire_burst` - انفجار نار شامل
3. `aether_pulse` - نبضة أثير بكل الاتجاهات
4. `phase_transition` - تحول انفجاري بين المراحل

---

## 🌍 أصول البيئة (Environment Assets)

### أرضيات الرماد | Ground Tiles
```
📁 assets/environment/
```

| الرقم | الاسم | الوصف | الحجم |
|------|-------|-------|------|
| 1 | `tile_ash_ground_a.glb` | أرض عادية | 1.1 KB |
| 2 | `tile_ash_ground_b.glb` | أرض مشققة | 1.1 KB |
| 3 | `tile_ash_ground_c.glb` | أرض بنار | 1.1 KB |
| 4 | `tile_ash_ground_d.glb` | أرض بضباب | 1.1 KB |

**الخصائص:**
- الأبعاد: 10 × 0.5 × 10
- قابلة للتكرار (Tileable)
- متوافقة مع نظام الشبكة

---

### النباتات | Vegetation
```
| الرقم | الاسم | النوع | الخصائص |
|------|-------|------|---------|
| 1 | `prop_burnt_tree_a.glb` | شجرة ملتوية | LOD enabled |
| 2 | `prop_burnt_tree_b.glb` | شجرة مجوفة | قابلة للتسلق |
| 3 | `prop_burnt_tree_c.glb` | شجرة ساقطة | عنصر بيئي |
```

---

### الصخور | Rock Clusters
```
| الرقم | الاسم | المادة | المقياس |
|------|-------|--------|---------|
| 1 | `prop_ash_rock_cluster_a.glb` | mat_ash_black | 2.0 |
| 2 | `prop_ash_rock_cluster_b.glb` | mat_aether_violet | 1.5 (متوهج) |
| 3 | `prop_ash_rock_cluster_c.glb` | mat_naris_fire | 1.8 (احترقاق) |
```

---

## ⚔️ الأسلحة (Weapons)

### 1. سيف القصيدة | Sword of Poem
```
📁 assets/weapons/sword_of_poem.json
⭐ الندرة: Legendary (أسطوري)
⚔️ الهجوم: 35 | السحر: 15
🎨 المواد: naris_fire (الشفرة), ancient_gold (المقبض)
💥 الضرر الخاص: 12 ضرر نار
```

**الهجمات:**
1. **قطعة خفيفة** - سريعة، 8 ضرر
2. **قطعة ثقيلة** - قوية، 18 ضرر
3. **انفجار النار** (خاص) - 25 ضرر، 20 تكلفة سحر

**الترقيات:**
- المستوى 3: هجوم +5
- المستوى 6: هجوم +8، ضرر نار +3
- المستوى 10: هجوم +12، ضرر نار +6، متوهج النار

---

### 2. قوس أنشودة الضباب | Bow of Mist Song
```
📁 assets/weapons/bow_mist_song.json
⭐ الندرة: Rare (نادر)
🏹 الهجوم: 28 | الرشاقة: 18 | السحر: 12
🎨 المواد: mist_cyan (الأطراف), aether_violet (الوتر)
💎 الضرر الخاص: 10 ضرر سحر
```

**أنواع الذخيرة:**
- السهم العادي: 8 ضرر
- سهم النار: 10 + 5 ضرر نار
- سهم الأثير: 12 + 8 ضرر سحر
- سهم الجليد: 10 + 6 ضرر جليد

---

## 🛡️ المعدات (Equipment)

### درع الرماد المعدني | Ash Plate Armor
```
📁 assets/equipment/armor_ash_plate.json
🎭 النوع: Heavy Armor (درع ثقيل)
🛡️ الدفاع: 28 | الدفاع السحري: 8 | Poise: 35
⚖️ الوزن: 18.0 (يؤثر على سرعة الحركة)
🎨 المواد: ash_black (الأساسي), ancient_gold (التزيينات)
```

**المقاومة:**
- النار: +10% (مقاوم)
- السحر: -10% (ضعيف)
- الفراغ: معادل

**فتحات التخصيص:**
- 2 فتحة رون (صدر)
- 2 فتحة جوهرة (الأكتاف)

**الترقيات:**
- تعزيز 1: دفاع +5
- تعزيز 2: دفاع +8، Poise +8
- تسريب الأثير: دفاع +12، دفاع سحري +8

---

## ✨ التأثيرات البصرية (VFX)

### مكتبة التأثيرات | VFX Library
```
📁 assets/vfx/fx_catalog.json
```

| الرقم | المعرّف | الاسم | الفئة | المدة |
|------|---------|-------|-------|------|
| 1 | `fx_sword_fire_burst` | انفجار نار السيف | weapon_attack | 1.5s |
| 2 | `fx_mist_arrow` | سهم الضباب | projectile | 3.0s |
| 3 | `fx_aether_pulse` | نبضة الأثير | magic_spell | 0.8s |
| 4 | `fx_phase_transition` | انتقال المرحلة | boss_ability | 2.0s |
| 5 | `fx_fire_fissure` | شقوق النار | boss_attack | متغير |
| 6 | `fx_mist_fog_plane` | مستوى الضباب | environment | مستمر |
| 7 | `fx_ember_particle_emitter` | مشع الجمرات | environment | مستمر |
| 8 | `fx_spirit_echo` | صدى الروح | companion | مستمر |
| 9 | `fx_heal_aura` | هالة الشفاء | spell | 2.5s |

**خصائص التأثيرات:**
- معدل الانبعاث: 50-200 جزيء/ثانية
- الشفافية الديناميكية: 0.5-0.8
- إضاءة حية (Light strength: 0.5-1.0)
- تصادم فيزيائي اختياري

---

## 🎮 واجهة المستخدم (UI)

### نظام الواجهة | UI System
```
📁 assets/ui/ui_elements.json
```

#### شرائط الحالة | Status Bars
- `hud_health_bar` - شريط الصحة (300×30)
- `hud_stamina_bar` - شريط الطاقة (300×20)
- `hud_mana_bar` - شريط السحر (300×20)

#### المخزون | Inventory
- `hud_inventory_slot` - فتحة مخزون (64×64)
- `hud_equipment_slot` - فتحة معدات (80×80)

#### المعلومات | Information
- `hud_status_effect` - أيقونة التأثير (48×48)
- `hud_minimap` - خريطة صغيرة (200×200)

#### السرد | Narrative
- `hud_dialogue_box` - صندوق الحوار (800×200)
- `hud_quest_marker` - علامة المهمة (3D waypoint)

#### القوائم | Menus
- `hud_main_menu` - القائمة الرئيسية
  - لعبة جديدة
  - متابعة
  - الإعدادات
  - خروج

---

## 📊 نظام المواد (Materials)

### مكتبة المواد الأساسية | Core Materials Library
```
📁 assets/materials/naris_materials.json
```

| المعرّف | الاسم | النوع | اللون | الإصدار |
|--------|-------|------|------|--------|
| `mat_naris_fire` | نار نارس | emissive | #ff6b35 | 1.5 |
| `mat_aether_violet` | أثير بنفسجي | emissive_metallic | #7b2cbf | 1.2 |
| `mat_mist_cyan` | ضباب سماوي | translucent | #00ffff | 0.7 |
| `mat_ancient_gold` | ذهب قديم | metallic | #d4a574 | 1.0 |
| `mat_ash_black` | رماد أسود | pbr_standard | #1a1a1a | 0.9 |

**خصائص الألوان:**
```
🔥 Orange Fire:    #ff6b35 (RGB: 255, 107, 53)
💜 Aether Purple:  #7b2cbf (RGB: 123, 44, 191)
💎 Cyan Mist:      #00ffff (RGB: 0, 255, 255)
🏆 Ancient Gold:   #d4a574 (RGB: 212, 165, 116)
🌑 Ash Black:      #1a1a1a (RGB: 26, 26, 26)
```

---

## 📦 تنسيقات الملفات

### GLB (Khronos glTF Binary)
```
✅ محرك Godot 4.x
✅ محرك Unity
✅ محركات ويب (Three.js, Babylon.js)
✅ Unreal Engine 5.x
```

### JSON (المواصفات)
```
✅ Human-readable
✅ Version control friendly
✅ Scalable
✅ Easy to modify
```

---

## 🚀 برامج النصية للتوليد

### 1. `generate_assets_python.py`
```
الحجم: 240 أسطر
الاستخدام: python3 generate_assets_python.py
الوظيفة: توليد GLB بسيط من JSON
الإخراج: 14 ملف GLB أساسي
```

**الميزات:**
- توليد أشكال هندسية (كبسولات، صناديق، طائرات)
- تطبيق مواد PBR
- تصدير GLB صحيح

---

### 2. `generate_assets_advanced.py`
```
الحجم: 420 أسطر
الاستخدام: python3 generate_assets_advanced.py
الوظيفة: توليد GLB متقدم مع هندسة معقدة
الإخراج: 4 نماذج متقدمة للشخصيات
```

**الميزات:**
- هندسة ديناميكية (كرات، كبسولات متعددة)
- شخصيات مع رأس وجذع وأطراف
- خرائط مواد معقدة
- محاكاة نسيج وخشونة

---

### 3. `generate_assets_blender.py` (للمستخدم المتقدم)
```
الاستخدام: blender --python generate_assets_blender.py
المتطلبات: Blender 3.0+
الميزات:
  - UV mapping تلقائي
  - تجميع مواد معقد
  - تصدير متعدد الصيغ (GLB, FBX, USDZ)
```

---

## 📁 هيكل المجلدات

```
assets/
├── characters/
│   ├── naris_hero.json
│   ├── naris_hero.glb
│   ├── naris_hero_advanced.glb
│   ├── spirit_wolf.json
│   ├── spirit_wolf.glb
│   ├── spirit_wolf_advanced.glb
│   ├── bone_beast.json
│   ├── bone_beast.glb
│   ├── bone_beast_advanced.glb
│   ├── ash_giant.json
│   ├── ash_giant.glb
│   └── ash_giant_advanced.glb
│
├── environment/
│   ├── ashen_forest_tiles.json
│   ├── tile_ash_ground_*.glb (4 ملفات)
│   ├── prop_burnt_tree_*.glb (3 ملفات)
│   └── prop_ash_rock_cluster_*.glb (3 ملفات)
│
├── weapons/
│   ├── sword_of_poem.json
│   └── bow_mist_song.json
│
├── equipment/
│   └── armor_ash_plate.json
│
├── vfx/
│   └── fx_catalog.json
│
├── ui/
│   └── ui_elements.json
│
├── materials/
│   └── naris_materials.json
│
└── scripts/
    ├── generate_assets_python.py
    ├── generate_assets_advanced.py
    └── generate_assets_blender.py
```

---

## 🔄 سير العمل | Workflow

### 1. إنشاء مواصفات JSON
```bash
# تحرير أو إضافة ملفات JSON للأصول الجديدة
vim assets/characters/my_character.json
```

### 2. توليد GLB
```bash
# إنشاء نماذج 3D من المواصفات
python3 assets/scripts/generate_assets_python.py

# إنشاء نماذج متقدمة
python3 assets/scripts/generate_assets_advanced.py
```

### 3. الاستيراد في المحرك
```
محرك Godot:
  1. انسخ ملفات .glb إلى res://assets/
  2. اضبط خصائص الاستيراد
  3. اسحب إلى المشهد

محرك Unity:
  1. انسخ إلى Assets/Models/
  2. تحديث اللواحق
  3. استخدم في Scenes
```

---

## 🎨 نظام الألوان NARIS

**القاعدة الذهبية:**
> "الخيال المظلم لا يعني عديم الألوان. كل إطار رئيسي يجب أن يتضمن: نار نارس + أثير بنفسجي + ضباب سماوي + ذهب قديم"

### مزيج اللون المثالي:
```
1. قاعدة البرتقالي المتوهج    #ff6b35 (نار)
2. لون ثانوي بنفسجي مشع      #7b2cbf (أثير)
3. لون ثالث سماوي شفاف        #00ffff (ضباب)
4. لون تجميل ذهبي              #d4a574 (ذهب)
5. خلفية سوداء داكنة            #1a1a1a (رماد)
```

---

## ✅ قائمة التحقق | Checklist

- [x] مواصفات JSON شاملة
- [x] نماذج GLB بسيطة (14)
- [x] نماذج GLB متقدمة (4)
- [x] أسلحة مع إحصائيات
- [x] معدات ودروع
- [x] نظام تأثيرات بصرية
- [x] عناصر واجهة المستخدم
- [x] برامج توليد Python
- [x] وثائق شاملة
- [ ] نسخ مواد عالية الدقة (اختياري)
- [ ] رسوم متحركة عظمية متقدمة (اختياري)

---

## 📞 الدعم والتوثيق

**الملفات ذات الصلة:**
- `CONCEPT_ART_AND_3D_ASSET_PROPOSAL.md` - الاقتراح الأصلي
- `3d-asset-viewer.html` - عارض تفاعلي
- `docs/NARIS_SRS.md` - مواصفات المتطلبات

---

**تم الإنشاء بواسطة:** Claude Code Assistant  
**الترخيص:** NARIS Project  
**آخر تحديث:** September 1, 2026
