#!/usr/bin/env python3
"""
NARIS Asset Generator - Pure Python GLB Generator
Generates 3D GLB models from JSON specifications without requiring Blender
Uses pygltflib for GLB export
"""

import json
import os
import struct
import math
from pathlib import Path

class SimpleGLBGenerator:
    """Generates simple GLB files from asset specifications"""

    def __init__(self, json_dir):
        self.json_dir = json_dir
        self.materials_spec = self._load_json(os.path.join(json_dir, 'materials', 'naris_materials.json'))

    def _load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_capsule_geometry(self, radius=0.5, height=2.0):
        """Create a capsule (cylinder with hemispherical caps)"""
        vertices = []
        indices = []

        # Top hemisphere (8 segments around, 4 segments up)
        segments = 8
        height_segments = 4

        # Top cap
        for i in range(height_segments + 1):
            angle_vert = (math.pi / 2) * (i / height_segments)
            y = radius * math.cos(angle_vert) + height / 2
            r = radius * math.sin(angle_vert)

            for j in range(segments):
                angle_horiz = (2 * math.pi * j) / segments
                x = r * math.cos(angle_horiz)
                z = r * math.sin(angle_horiz)
                vertices.append((x, y, z))

        # Bottom cap
        for i in range(height_segments + 1):
            angle_vert = (math.pi / 2) * (i / height_segments)
            y = -radius * math.cos(angle_vert) - height / 2
            r = radius * math.sin(angle_vert)

            for j in range(segments):
                angle_horiz = (2 * math.pi * j) / segments
                x = r * math.cos(angle_horiz)
                z = r * math.sin(angle_horiz)
                vertices.append((x, y, z))

        # Generate indices for triangles
        for cap in range(2):
            base_idx = cap * (height_segments + 1) * segments

            for i in range(height_segments):
                for j in range(segments):
                    a = base_idx + i * segments + j
                    b = base_idx + i * segments + (j + 1) % segments
                    c = base_idx + (i + 1) * segments + j
                    d = base_idx + (i + 1) * segments + (j + 1) % segments

                    indices.extend([a, b, c])
                    indices.extend([b, d, c])

        return vertices, indices

    def _create_box_geometry(self, width=2.0, height=3.0, depth=1.0):
        """Create a box geometry"""
        w, h, d = width / 2, height / 2, depth / 2

        vertices = [
            # Front face
            (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d),
            # Back face
            (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
        ]

        indices = [
            # Front
            0, 1, 2, 0, 2, 3,
            # Back
            5, 4, 7, 5, 7, 6,
            # Top
            3, 2, 6, 3, 6, 7,
            # Bottom
            4, 5, 1, 4, 1, 0,
            # Right
            1, 5, 6, 1, 6, 2,
            # Left
            4, 0, 3, 4, 3, 7,
        ]

        return vertices, indices

    def _create_plane_geometry(self, width=10.0, depth=10.0):
        """Create a plane geometry"""
        w, d = width / 2, depth / 2

        vertices = [
            (-w, 0, -d), (w, 0, -d), (w, 0, d), (-w, 0, d)
        ]

        indices = [0, 1, 2, 0, 2, 3]

        return vertices, indices

    def _color_to_rgba(self, color_list):
        """Convert RGB list to RGBA tuple"""
        r, g, b = color_list
        return (int(r * 255), int(g * 255), int(b * 255), 255)

    def _create_gltf_json(self, name, vertices, indices, material_id):
        """Create a minimal glTF JSON structure"""
        # Flatten vertices for binary buffer
        vertex_data = []
        for v in vertices:
            vertex_data.extend(v)

        # Create binary blob
        vertex_bytes = struct.pack(f'{len(vertex_data)}f', *vertex_data)
        index_bytes = struct.pack(f'{len(indices)}H', *indices)

        # Combine buffers
        combined_data = vertex_bytes + index_bytes

        material_spec = next((m for m in self.materials_spec['materials'] if m['id'] == material_id), None)

        if material_spec:
            base_color = material_spec['properties'].get('base_color', [0.5, 0.5, 0.5])
            emission = material_spec['properties'].get('emission', [0, 0, 0]) if material_spec.get('type') in ['emissive', 'emissive_metallic'] else [0, 0, 0]
            metallic = material_spec['properties'].get('metallic', 0.0)
            roughness = material_spec['properties'].get('roughness', 0.5)
        else:
            base_color = [0.5, 0.5, 0.5]
            emission = [0, 0, 0]
            metallic = 0.0
            roughness = 0.5

        gltf = {
            "asset": {
                "generator": "NARIS Asset Generator",
                "version": "2.0"
            },
            "scene": 0,
            "scenes": [{
                "nodes": [0]
            }],
            "nodes": [{
                "mesh": 0,
                "name": name
            }],
            "meshes": [{
                "primitives": [{
                    "attributes": {
                        "POSITION": 0
                    },
                    "indices": 1,
                    "material": 0
                }],
                "name": name
            }],
            "materials": [{
                "name": material_id,
                "pbrMetallicRoughness": {
                    "baseColorFactor": base_color + [1.0],
                    "metallicFactor": metallic,
                    "roughnessFactor": roughness
                },
                "emissiveFactor": emission
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,  # FLOAT
                    "count": len(vertices),
                    "type": "VEC3",
                    "min": [min(v[0] for v in vertices), min(v[1] for v in vertices), min(v[2] for v in vertices)],
                    "max": [max(v[0] for v in vertices), max(v[1] for v in vertices), max(v[2] for v in vertices)]
                },
                {
                    "bufferView": 1,
                    "componentType": 5123,  # UNSIGNED_SHORT
                    "count": len(indices),
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {
                    "buffer": 0,
                    "byteLength": len(vertex_bytes),
                    "byteOffset": 0,
                    "target": 34962  # ARRAY_BUFFER
                },
                {
                    "buffer": 0,
                    "byteLength": len(index_bytes),
                    "byteOffset": len(vertex_bytes),
                    "target": 34963  # ELEMENT_ARRAY_BUFFER
                }
            ],
            "buffers": [{
                "byteLength": len(combined_data)
            }]
        }

        return gltf, combined_data

    def _write_glb(self, filepath, gltf_json, binary_data):
        """Write glTF data as GLB file"""
        json_str = json.dumps(gltf_json)
        json_bytes = json_str.encode('utf-8')

        # Pad JSON to 4-byte alignment
        json_padding = (4 - (len(json_bytes) % 4)) % 4
        json_bytes += b' ' * json_padding

        # GLB header
        magic = b'glTF'
        version = struct.pack('<I', 2)

        # JSON chunk
        json_length = struct.pack('<I', len(json_bytes))
        json_type = b'JSON'

        # Binary chunk
        binary_length = struct.pack('<I', len(binary_data))
        binary_type = b'BIN\x00'

        # Calculate total file size
        header_size = 12
        json_chunk_size = 8 + len(json_bytes)
        binary_chunk_size = 8 + len(binary_data)
        total_size = struct.pack('<I', header_size + json_chunk_size + binary_chunk_size)

        # Write file
        with open(filepath, 'wb') as f:
            f.write(magic)
            f.write(version)
            f.write(total_size)
            f.write(json_length)
            f.write(json_type)
            f.write(json_bytes)
            f.write(binary_length)
            f.write(binary_type)
            f.write(binary_data)

        print(f"✓ Exported: {filepath}")

    def generate_character(self, char_spec, output_path):
        """Generate a character model"""
        char_name = char_spec['name']
        print(f"Generating character: {char_name}")

        # Get primary material
        materials = char_spec.get('materials', {})
        primary_material = materials.get('body', 'mat_ash_black')

        # Create geometry based on type
        char_type = char_spec.get('type', 'character')
        if char_type == 'boss':
            vertices, indices = self._create_box_geometry(2, 3, 1)
        else:
            vertices, indices = self._create_capsule_geometry(0.5, 2)

        # Create GLB
        gltf_json, binary_data = self._create_gltf_json(char_name, vertices, indices, primary_material)
        self._write_glb(output_path, gltf_json, binary_data)

    def generate_environment_tile(self, tile_spec, output_path):
        """Generate an environment tile"""
        tile_name = tile_spec['name']
        print(f"Generating tile: {tile_name}")

        dims = tile_spec.get('dimensions', {'x': 10, 'y': 0.5, 'z': 10})
        vertices, indices = self._create_box_geometry(dims['x'], dims['y'], dims['z'])

        material_id = tile_spec.get('material', 'mat_ash_black')

        gltf_json, binary_data = self._create_gltf_json(tile_name, vertices, indices, material_id)
        self._write_glb(output_path, gltf_json, binary_data)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, '..')

    generator = SimpleGLBGenerator(assets_dir)

    # Generate characters
    char_specs = [
        'naris_hero.json',
        'spirit_wolf.json',
        'bone_beast.json',
        'ash_giant.json',
    ]

    for char_file in char_specs:
        char_path = os.path.join(assets_dir, 'characters', char_file)
        if os.path.exists(char_path):
            with open(char_path, 'r', encoding='utf-8') as f:
                char_spec = json.load(f)

            output_path = char_path.replace('.json', '.glb')
            generator.generate_character(char_spec, output_path)

    # Generate environment tiles
    env_path = os.path.join(assets_dir, 'environment', 'ashen_forest_tiles.json')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_spec = json.load(f)

        # Generate ground tiles
        for tile in env_spec['tiles'].get('ground', []):
            output_path = os.path.join(assets_dir, 'environment', f"{tile['id']}.glb")
            generator.generate_environment_tile(tile, output_path)

        # Generate vegetation
        for tree in env_spec['tiles'].get('vegetation', []):
            output_path = os.path.join(assets_dir, 'environment', f"{tree['id']}.glb")
            generator.generate_environment_tile(tree, output_path)

        # Generate rocks
        for rock in env_spec['tiles'].get('rocks', []):
            output_path = os.path.join(assets_dir, 'environment', f"{rock['id']}.glb")
            generator.generate_environment_tile(rock, output_path)

    print("\n✓ All assets generated successfully!")

if __name__ == '__main__':
    main()
