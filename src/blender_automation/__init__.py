"""
NAR: Chronicles of the Fallen Star - Blender Asset Automation Framework
========================================================================

A comprehensive Python framework for automating the asset production pipeline in Blender.
Handles LOD generation, PBR baking, UV unwrapping, retopology, and texture streaming.

Version: 1.0.0
License: Proprietary
"""

__version__ = "1.0.0"
__author__ = "NARIS Development Team"

from . import config
from . import lod_generator
from . import pbr_baker
from . import uv_automation
from . import retopology_tools
from . import batch_processor

__all__ = [
    'config',
    'lod_generator',
    'pbr_baker',
    'uv_automation',
    'retopology_tools',
    'batch_processor',
]
