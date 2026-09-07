#!/usr/bin/env python3
"""
NAR Blender Asset Automation Framework - Setup Script
Installation and configuration for production asset pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="nar-blender-automation",
    version="1.0.0",
    author="NAR Chronicles Development",
    description="Production-ready Blender asset automation framework for game development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h-alnami/hhj",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies (mostly bundled with Blender)
        # Uncomment if using outside Blender environment
        # "numpy>=1.19.0",
        # "Pillow>=7.0.0",
    ],
    extras_require={
        "cloud": [
            "requests>=2.25.0",
            "boto3>=1.17.0",
            "aiohttp>=3.7.0",
        ],
        "monitoring": [
            "prometheus-client>=0.9.0",
        ],
        "database": [
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.8.0",
        ],
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "blender-asset-pipeline=blender_automation.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="blender game-development asset-pipeline lod pbr uv retopology",
    project_urls={
        "Documentation": "https://github.com/h-alnami/hhj/tree/main/src/blender_automation",
        "Source": "https://github.com/h-alnami/hhj",
        "Bug Reports": "https://github.com/h-alnami/hhj/issues",
    },
)
