# NARIS — Concept Art & Proposed 3D Asset List

**Project:** NARIS / Call of Naris
**Studio:** NARIS Studios
**Company:** Alnami Company
**Document Type:** Character concept art (2D reference) + proposed 3D production asset list
**Status:** Draft for Concept Artist / Technical Artist review

This document delivers two things requested for the next art pass:

1. Anime-style 2D concept art for the game's main cast and key environment, generated as
   a visual reference ahead of full 3D modeling (per the **Concept Artist** handoff in
   `README.md` §7: *"Final hero, Spirit Wolf, Bone Beast, Ash Giant, Mist Guardian, Ashen
   Forest"*).
2. A proposed list of the 3D assets — characters, environment tiles/modules, materials,
   and props — that should be produced from this concept art, in the formats already used
   by the project's asset pipeline (GLB / USDZ / STL).

All concept art follows the mandatory NARIS color bible from `README.md` / `docs/SRS.md`:
**Naris Fire** (orange/ember), **Aether Violet**, **Mist Cyan**, **Ancient Gold**, **Ash
Black** — saturated, never gray-only (NFR-005).

---

## 1. Concept Art (2D reference, anime style)

Generated via Canva AI design generation. Each entry links to 4 candidate designs in
Canva — pick the strongest read per character, then use `create-design-from-candidate`
to save the chosen one to the account before export.

| Character / Scene | Role | Candidate designs |
|---|---|---|
| **Naris** (hero) | Playable protagonist, wields the Sword of Poem | [Candidate 1](https://www.canva.com/d/YF5eLwoT9HTIfRy) · [2](https://www.canva.com/d/AiuAVe1aSl-QSVD) · [3](https://www.canva.com/d/vNQkn7nCWgqatAY) · [4](https://www.canva.com/d/YZpS2KpzvvFDAWQ) |
| **Spirit Wolf** | Companion creature (Bond / Echo Link system) | [Candidate 1](https://www.canva.com/d/l1N5SuK-fxn0DMs) · [2](https://www.canva.com/d/gbfdeUiLXoYI3Qy) · [3](https://www.canva.com/d/PqSlEQFNDd1KGVF) · [4](https://www.canva.com/d/EfURy7QnD4I8ycT) |
| **Bone Beast** | Early enemy (prologue quest target) | [Candidate 1](https://www.canva.com/d/DyBISTODU0xA8LQ) · [2](https://www.canva.com/d/zJE0AwfUnWRXyVt) · [3](https://www.canva.com/d/m59JNYKa7rQZ0fv) · [4](https://www.canva.com/d/DcYtf9PvGVcTBCc) |
| **Ash Giant** | Boss (multi-phase, Ash Gate encounter) | [Candidate 1](https://www.canva.com/d/Nvl62uVD1AtOIke) · [2](https://www.canva.com/d/QWaeXxNeizJxORr) · [3](https://www.canva.com/d/KgJRtsgjwzme5CQ) · [4](https://www.canva.com/d/-58_wh_uj_jKJO4) |
| **Ashen Forest** | Opening zone environment key art | [Candidate 1](https://www.canva.com/d/TO-UcviiSEOekXu) · [2](https://www.canva.com/d/nd2WZVZ--DPvxCZ) · [3](https://www.canva.com/d/WP_iD2TtDyJsZ5R) · [4](https://www.canva.com/d/7xzaumNBtiymwM3) |

**Not yet generated** (from the same handoff list, pending art budget/credits):
Mist Guardian.

> Note: the previous image-generation credits (Gamma) were exhausted (HTTP 402) when this
> pass ran; the above set was produced with Canva instead. Re-run with Gamma once billing
> is refilled for tighter control over aspect ratio and style consistency across the set.

---

## 2. Proposed 3D Character Assets

Mirrors the existing 3D pipeline used elsewhere in this project (GLB for the Godot
engine, USDZ for AR/mobile preview, STL only if a physical print is ever needed).

| Asset | Source concept | Notes for modeler | Priority |
|---|---|---|---|
| `naris_hero.glb` | Naris concept art | Rigged humanoid, cloak + armor with cloth sim bones, Sword of Poem as a separate attachable mesh (see §4 upgrade tiers) | High — playable character |
| `spirit_wolf.glb` | Spirit Wolf concept art | Quadruped rig, semi-transparent shader (see §3 materials), particle attach points at spine and eyes | High — companion system (FR-080/081) |
| `bone_beast.glb` | Bone Beast concept art | Quadruped rig, exposed-bone material, poise-break VFX socket on the head | Medium — prologue enemy |
| `ash_giant.glb` | Ash Giant concept art | Multi-phase boss rig (phase-2 needs a "cracked/molten" material variant per FR-140) | Medium — boss encounter |
| `mist_guardian.glb` | *(concept art pending)* | Bipedal or serpentine — TBD once concept art exists | Low — later boss |

Each character should also get a `.usdz` export alongside the `.glb` for the same AR/mobile
preview workflow already used by the other 3D assets in this project.

---

## 3. Proposed Environment Tiles & Modular Kit ("بلاطات" — tiles)

A modular Ashen Forest tile/prop kit, built once and reused across the region (matches
`FR-100` World Map / region system):

| Tile / module | Purpose |
|---|---|
| `tile_ash_ground_[a-d].glb` | 4 variants of scorched forest floor, tileable edges |
| `prop_burnt_tree_[a-c].glb` | Twisted burnt trees, LOD-friendly, wind-sway bone |
| `prop_ash_rock_cluster_[a-c].glb` | Rock/debris clutter for set dressing |
| `structure_ash_gate.glb` | The sealed Ash Gate — hero + rune-glow material, drives quest objective 5 (FR-042) |
| `fx_ember_particle_emitter.glb` | Reusable ember/ash particle mesh anchor for the VFX spawner |
| `fx_mist_fog_plane.glb` | Ground-hugging cyan mist plane, matches Mist Cyan atmosphere |

---

## 4. Proposed Materials / Shaders (shared across all assets)

One shared material library so every character and tile reads as the same world:

| Material | Look | Used on |
|---|---|---|
| `mat_naris_fire` | Emissive orange/ember, animated flicker | Sword of Poem, ember particles, hero fire aura |
| `mat_aether_violet` | Emissive saturated violet, soft glow falloff | Aether energy effects, Ash Giant core, hero hand glow |
| `mat_mist_cyan` | Translucent, rim-lit fog cyan | Spirit Wolf body, fog planes, spectral rim light on all characters |
| `mat_ancient_gold` | Metallic gold, high specular | Armor trim, Ash Gate runes, UI-adjacent props |
| `mat_ash_black` | Matte near-black PBR base | Base armor, Bone Beast sinew, Ash Giant body |

---

## 5. Proposed Props

| Prop | Notes |
|---|---|
| `sword_of_poem_dormant.glb` | Upgrade tier 1 (Dormant Blade) |
| `sword_of_poem_ember.glb` | Upgrade tier 2 (Ember Cut) — `mat_naris_fire` active |
| `sword_of_poem_aether.glb` | Upgrade tier 3 (Aether Verse) — `mat_aether_violet` active |
| `sword_of_poem_resonance.glb` | Upgrade tier 4 (Naris Resonance) — all materials active, highest glow |
| `item_memory_crystal.glb` | Quest item, small hero prop, `mat_aether_violet` |
| `item_silent_flask.glb` | Starting inventory item (FR-054) |

---

## 6. Suggested Directory Layout

Matches the `assets/` structure already required for the v1.9 Unified Integration Build
(`docs/SRS.md` §9):

```txt
assets/
  characters/
    naris_hero.glb / .usdz
    spirit_wolf.glb / .usdz
    bone_beast.glb / .usdz
    ash_giant.glb / .usdz
  environment/
    tile_ash_ground_a.glb ... tile_ash_ground_d.glb
    prop_burnt_tree_a.glb ... prop_burnt_tree_c.glb
    prop_ash_rock_cluster_a.glb ... c.glb
    structure_ash_gate.glb
  fx/
    fx_ember_particle_emitter.glb
    fx_mist_fog_plane.glb
  props/
    sword_of_poem_dormant.glb ... resonance.glb
    item_memory_crystal.glb
    item_silent_flask.glb
  materials/
    mat_naris_fire, mat_aether_violet, mat_mist_cyan, mat_ancient_gold, mat_ash_black
```

---

## 7. Next Steps

1. Concept Artist: review the 5 candidate sets above, pick final direction per character,
   and produce a Mist Guardian concept pass.
2. Technical Artist: build the 5 shared materials first (§4) — every character and tile
   depends on them for a consistent, non-gray, saturated look (NFR-005).
3. 3D Artist: model characters in priority order (§2), export `.glb` + `.usdz` per asset.
4. Re-run AI concept art generation once Gamma image credits are refilled, for a
   consistent single-model style pass across the full cast.
