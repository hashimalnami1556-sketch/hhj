#!/usr/bin/env python3
"""
NARIS Asset Generator - Blender Python Script
Generates 3D models from JSON specifications using Blender API
"""

import bpy
import json
import os
from mathutils import Vector, Euler

class NARISAssetGenerator:
    def __init__(self, json_path):
        self.json_data = self._load_json(json_path)
        self.materials = {}
        self._setup_materials()

    def _load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _setup_materials(self):
        """Create Blender materials from JSON spec"""
        for mat_spec in self.json_data.get('materials', []):
            mat = bpy.data.materials.new(name=mat_spec['id'])
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes['Principled BSDF']

            props = mat_spec.get('properties', {})

            # Set base color
            if 'base_color' in props:
                rgb = props['base_color']
                bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)

            # Set metallic and roughness
            if 'metallic' in props:
                bsdf.inputs['Metallic'].default_value = props['metallic']
            if 'roughness' in props:
                bsdf.inputs['Roughness'].default_value = props['roughness']

            # Set emission for emissive materials
            if mat_spec.get('type') in ['emissive', 'emissive_metallic']:
                if 'emission' in props:
                    rgb = props['emission']
                    bsdf.inputs['Emission'].default_value = (*rgb, 1.0)
                if 'emission_strength' in props:
                    bsdf.inputs['Emission Strength'].default_value = props['emission_strength']

            self.materials[mat_spec['id']] = mat

    def generate_character(self, char_spec):
        """Generate a character mesh from specification"""
        char_name = char_spec['name']
        print(f"Generating character: {char_name}")

        # Create armature (skeleton)
        armature = bpy.data.armatures.new(f"{char_name}_Armature")
        armature_obj = bpy.data.objects.new(f"{char_name}_Armature", armature)
        bpy.context.collection.objects.link(armature_obj)
        bpy.context.view_layer.objects.active = armature_obj
        armature_obj.select_set(True)

        # Enter edit mode to add bones
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature.edit_bones

        bones = char_spec.get('model', {}).get('bones', [])
        for bone_name in bones:
            bone = edit_bones.new(bone_name)
            bone.head = Vector((0, 0, 0))
            bone.tail = Vector((0, 0.1, 0))

        bpy.ops.object.mode_set(mode='OBJECT')

        # Create mesh
        mesh = bpy.data.meshes.new(f"{char_name}_Mesh")
        mesh_obj = bpy.data.objects.new(char_name, mesh)
        bpy.context.collection.objects.link(mesh_obj)

        # Create basic mesh (cube placeholder)
        verts = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 3, 7, 4), (1, 2, 6, 5)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        # Apply armature modifier
        armature_mod = mesh_obj.modifiers.new(f"{char_name}_Armature", 'ARMATURE')
        armature_mod.object = armature_obj

        # Apply materials
        materials_spec = char_spec.get('materials', {})
        for material_id in materials_spec.values():
            if material_id in self.materials:
                mesh_obj.data.materials.append(self.materials[material_id])

        return mesh_obj

    def generate_environment_tile(self, tile_spec):
        """Generate an environment tile"""
        tile_name = tile_spec['name']
        print(f"Generating tile: {tile_name}")

        mesh = bpy.data.meshes.new(f"{tile_name}_Mesh")
        obj = bpy.data.objects.new(tile_name, mesh)
        bpy.context.collection.objects.link(obj)

        # Create quad plane with dimensions
        dims = tile_spec.get('dimensions', {'x': 10, 'y': 0.5, 'z': 10})
        x, y, z = dims['x']/2, dims['y']/2, dims['z']/2

        verts = [
            (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
            (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 3, 7, 4), (1, 2, 6, 5)
        ]

        mesh.from_pydata(verts, [], faces)
        mesh.update()

        # Apply material
        material_id = tile_spec.get('material')
        if material_id in self.materials:
            obj.data.materials.append(self.materials[material_id])

        return obj

    def export_glb(self, obj, filename):
        """Export object as GLB"""
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=filename,
            use_selection=True,
            export_format='GLB'
        )
        print(f"Exported: {filename}")

def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, '..')

    # Load character specs
    char_specs = [
        os.path.join(assets_dir, 'characters', 'naris_hero.json'),
        os.path.join(assets_dir, 'characters', 'spirit_wolf.json'),
    ]

    # Generate assets
    for char_path in char_specs:
        if os.path.exists(char_path):
            with open(char_path, 'r', encoding='utf-8') as f:
                char_spec = json.load(f)

            generator = NARISAssetGenerator(
                os.path.join(assets_dir, 'materials', 'naris_materials.json')
            )

            # Generate mesh
            obj = generator.generate_character(char_spec)

            # Export
            output_path = char_path.replace('.json', '.glb')
            generator.export_glb(obj, output_path)

if __name__ == '__main__':
    main()
