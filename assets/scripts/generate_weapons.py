#!/usr/bin/env python3
"""Generate GLB models for all weapons from JSON specifications."""

import json
import struct
import math
from pathlib import Path

class WeaponModelGenerator:
    """Generates GLB models for weapon assets."""

    def __init__(self):
        self.weapons_dir = Path("/home/user/hhj/assets/weapons")
        self.output_dir = Path("/home/user/hhj/assets/models/weapons")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_box_geometry(self, width, height, depth, color_rgb):
        """Create a box geometry with given dimensions and color."""
        w, h, d = width/2, height/2, depth/2

        vertices = [
            # Front face
            -w, -h, d,  w, -h, d,  w, h, d,  -w, h, d,
            # Back face
            -w, -h, -d,  -w, h, -d,  w, h, -d,  w, -h, -d,
            # Top face
            -w, h, -d,  -w, h, d,  w, h, d,  w, h, -d,
            # Bottom face
            -w, -h, -d,  w, -h, -d,  w, -h, d,  -w, -h, d,
            # Right face
            w, -h, -d,  w, h, -d,  w, h, d,  w, -h, d,
            # Left face
            -w, -h, -d,  -w, -h, d,  -w, h, d,  -w, h, -d,
        ]

        indices = [
            # Front
            0, 1, 2,  0, 2, 3,
            # Back
            4, 6, 5,  4, 7, 6,
            # Top
            8, 9, 10,  8, 10, 11,
            # Bottom
            12, 13, 14,  12, 14, 15,
            # Right
            16, 17, 18,  16, 18, 19,
            # Left
            20, 21, 22,  20, 22, 23,
        ]

        colors = []
        for _ in range(24):
            colors.extend([color_rgb[0]/255, color_rgb[1]/255, color_rgb[2]/255, 1.0])

        return vertices, indices, colors

    def _create_capsule_geometry(self, radius, height, color_rgb):
        """Create a capsule geometry for handles and shafts."""
        segments = 12
        rings = 4

        vertices = []
        indices = []

        # Top hemisphere
        h_half = height / 2
        for ring in range(rings + 1):
            phi = (ring / rings) * (math.pi / 2)
            ring_radius = radius * math.sin(phi)
            ring_height = h_half - radius * (1 - math.cos(phi))

            for seg in range(segments):
                theta = (seg / segments) * 2 * math.pi
                x = ring_radius * math.cos(theta)
                z = ring_radius * math.sin(theta)
                vertices.extend([x, ring_height, z])

        # Bottom hemisphere
        for ring in range(rings + 1):
            phi = (ring / rings) * (math.pi / 2)
            ring_radius = radius * math.sin(phi)
            ring_height = -h_half + radius * (1 - math.cos(phi))

            for seg in range(segments):
                theta = (seg / segments) * 2 * math.pi
                x = ring_radius * math.cos(theta)
                z = ring_radius * math.sin(theta)
                vertices.extend([x, ring_height, z])

        # Generate indices
        for ring in range(2 * rings):
            for seg in range(segments):
                a = ring * segments + seg
                b = ring * segments + ((seg + 1) % segments)
                c = (ring + 1) * segments + ((seg + 1) % segments)
                d = (ring + 1) * segments + seg

                indices.extend([a, b, c])
                indices.extend([a, c, d])

        colors = []
        for _ in range(len(vertices) // 3):
            colors.extend([color_rgb[0]/255, color_rgb[1]/255, color_rgb[2]/255, 1.0])

        return vertices, indices, colors

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_glb(self, vertices, indices, colors, name):
        """Create a GLB file from vertices, indices, and colors."""
        # Prepare mesh data
        vertex_count = len(vertices) // 3
        index_count = len(indices)

        # Create binary data
        vertex_data = struct.pack(f'{len(vertices)}f', *vertices)
        index_data = struct.pack(f'{len(indices)}H', *indices)
        color_data = struct.pack(f'{len(colors)}f', *colors)

        # Create glTF JSON
        gltf_json = {
            "asset": {"version": "2.0"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [
                {
                    "name": name,
                    "mesh": 0,
                    "translation": [0, 0, 0],
                    "rotation": [0, 0, 0, 1],
                    "scale": [1, 1, 1]
                }
            ],
            "meshes": [{
                "name": name,
                "primitives": [{
                    "attributes": {
                        "POSITION": 0,
                        "COLOR_0": 1
                    },
                    "indices": 2,
                    "material": 0
                }]
            }],
            "materials": [{
                "name": "Material",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [1, 1, 1, 1],
                    "metallicFactor": 0.5,
                    "roughnessFactor": 0.7
                }
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": vertex_count,
                    "type": "VEC3"
                },
                {
                    "bufferView": 1,
                    "componentType": 5126,
                    "count": vertex_count,
                    "type": "VEC4"
                },
                {
                    "bufferView": 2,
                    "componentType": 5125,
                    "count": index_count,
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteStride": 12},
                {"buffer": 0, "byteOffset": len(vertex_data), "byteStride": 16},
                {"buffer": 0, "byteOffset": len(vertex_data) + len(color_data)}
            ],
            "buffers": [{"byteLength": len(vertex_data) + len(color_data) + len(index_data)}]
        }

        import json as json_module
        gltf_str = json_module.dumps(gltf_json)
        gltf_bytes = gltf_str.encode('utf-8')

        # Padding
        gltf_len = len(gltf_bytes)
        padding = (4 - (gltf_len % 4)) % 4
        gltf_bytes += b' ' * padding

        bin_data = vertex_data + color_data + index_data
        bin_padding = (4 - (len(bin_data) % 4)) % 4
        bin_data += b'\x00' * bin_padding

        # GLB header
        glb = b'glTF'
        glb += struct.pack('<I', 2)  # Version 2
        glb += struct.pack('<I', 28 + len(gltf_bytes) + len(bin_data))  # Total size

        # JSON chunk
        glb += struct.pack('<I', len(gltf_bytes))
        glb += b'JSON'
        glb += gltf_bytes

        # Binary chunk
        glb += struct.pack('<I', len(bin_data))
        glb += b'BIN\x00'
        glb += bin_data

        return glb

    def generate_all_weapons(self):
        """Generate GLB models for all weapons."""
        if not self.weapons_dir.exists():
            print(f"Weapons directory not found: {self.weapons_dir}")
            return

        weapon_files = sorted(self.weapons_dir.glob("*.json"))
        print(f"Found {len(weapon_files)} weapon specifications")

        for weapon_file in weapon_files:
            try:
                with open(weapon_file, 'r', encoding='utf-8') as f:
                    weapon_data = json.load(f)

                weapon_id = weapon_data.get('id')
                weapon_type = weapon_data.get('type', 'sword')
                attack = weapon_data.get('stats', {}).get('attack', 20)

                # Color mapping based on rarity
                rarity = weapon_data.get('rarity', 'common')
                rarity_colors = {
                    'common': (169, 169, 169),      # Gray
                    'uncommon': (34, 139, 34),     # Green
                    'rare': (0, 100, 200),          # Blue
                    'legendary': (255, 215, 0)     # Gold
                }
                color = rarity_colors.get(rarity, (150, 150, 150))

                # Generate geometry based on weapon type
                if weapon_type in ['sword', 'dagger', 'spear']:
                    blade_height = 2.0 + (attack / 30)
                    blade_width = 0.3 + (attack / 100)
                    vertices, indices, colors = self._create_box_geometry(
                        blade_width, blade_height, 0.15, color
                    )

                    # Add handle
                    handle_v, handle_i, handle_c = self._create_capsule_geometry(
                        0.1, 0.8, (139, 90, 43)
                    )
                    offset = len(vertices) // 3
                    vertices.extend(handle_v)
                    indices.extend([i + offset for i in handle_i])
                    colors.extend(handle_c)

                elif weapon_type in ['axe', 'mace', 'hammer']:
                    head_size = 0.5 + (attack / 50)
                    vertices, indices, colors = self._create_box_geometry(
                        head_size, head_size, head_size, color
                    )

                    handle_v, handle_i, handle_c = self._create_capsule_geometry(
                        0.12, 1.2, (139, 90, 43)
                    )
                    offset = len(vertices) // 3
                    vertices.extend(handle_v)
                    indices.extend([i + offset for i in handle_i])
                    colors.extend(handle_c)

                elif weapon_type == 'bow':
                    vertices, indices, colors = self._create_capsule_geometry(
                        0.08, 1.5, color
                    )

                elif weapon_type == 'staff':
                    vertices, indices, colors = self._create_capsule_geometry(
                        0.12, 2.0, color
                    )

                elif weapon_type == 'wand':
                    vertices, indices, colors = self._create_capsule_geometry(
                        0.08, 1.2, color
                    )

                elif weapon_type == 'claws':
                    vertices, indices, colors = self._create_capsule_geometry(
                        0.06, 0.3, color
                    )

                elif weapon_type == 'scythe':
                    vertices, indices, colors = self._create_box_geometry(
                        0.2, 1.8, 1.0, color
                    )

                elif weapon_type == 'whip':
                    vertices, indices, colors = self._create_capsule_geometry(
                        0.05, 1.5, color
                    )

                else:
                    vertices, indices, colors = self._create_box_geometry(
                        0.3, 1.0, 0.2, color
                    )

                # Create GLB
                glb_data = self._create_glb(vertices, indices, colors, weapon_id)

                # Save GLB
                output_path = self.output_dir / f"{weapon_id}.glb"
                with open(output_path, 'wb') as f:
                    f.write(glb_data)

                print(f"✓ Generated {weapon_id} ({weapon_type})")

            except Exception as e:
                print(f"✗ Error processing {weapon_file.name}: {e}")

        print(f"\nAll weapon models saved to {self.output_dir}")

if __name__ == "__main__":
    generator = WeaponModelGenerator()
    generator.generate_all_weapons()
