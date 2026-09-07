# NAR Blender Asset Automation Framework - Docker Image
# Production-ready containerized asset pipeline for game development

FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

LABEL maintainer="NAR Chronicles Development"
LABEL description="Production Blender asset automation framework for AAA game development"
LABEL version="1.0.0"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV BLENDER_VERSION=4.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Core utilities
    curl \
    wget \
    git \
    # Python runtime
    python3 \
    python3-pip \
    python3-dev \
    # Build tools
    build-essential \
    # Blender dependencies
    libxi6 \
    libxrender1 \
    libxkbcommon0 \
    libssl-dev \
    libffi-dev \
    # Image processing
    libopenjp2-7 \
    # Optional: Rendering support
    libcuda1 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender (headless version suitable for rendering)
RUN mkdir -p /opt/blender && cd /opt/blender && \
    wget https://download.blender.org/release/Blender4.0/blender-4.0.0-linux-x64.tar.xz && \
    tar -xf blender-4.0.0-linux-x64.tar.xz && \
    ln -s /opt/blender/blender-4.0.0-linux-x64/blender /usr/local/bin/blender && \
    rm blender-4.0.0-linux-x64.tar.xz

# Install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel

# Create working directory
WORKDIR /workspace

# Copy application
COPY . /workspace/

# Install the asset pipeline package
RUN cd /workspace && python3 setup.py develop

# Create required directories
RUN mkdir -p /workspace/assets/source \
    /workspace/exports \
    /workspace/configs \
    /workspace/logs

# Verify installation
RUN python3 -c "from src.blender_automation.config import BlenderAssetPipelineConfig; print('✓ Pipeline installed')"

# Set Blender path
ENV BLENDER_PATH=/usr/local/bin/blender

# Default command: production workflow
ENTRYPOINT ["python3"]
CMD ["src/blender_automation/production_workflow.py", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "from src.blender_automation.main import NARAssetPipeline; print('healthy')" || exit 1
