#!/bin/bash
# NAR Blender Asset Automation Framework - Unix Launch Script
# Bash script for easy asset processing on macOS and Linux

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=${1:-help}
INPUT=""
ASSET_NAME=""
CATEGORY=""
CONFIG=""
THREADS=4
BATCH_SIZE=5

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
write_status() {
    local status=$1
    local message=$2
    case $status in
        Success) echo -e "${GREEN}[✓]${NC} $message" ;;
        Error) echo -e "${RED}[✗]${NC} $message" >&2 ;;
        Warning) echo -e "${YELLOW}[!]${NC} $message" ;;
        Info) echo -e "${CYAN}[*]${NC} $message" ;;
    esac
}

verify_blender() {
    write_status "Info" "Checking Blender installation..."

    local blender_path="${BLENDER_PATH:-blender}"

    if ! command -v "$blender_path" &> /dev/null; then
        write_status "Error" "Blender not found at '$blender_path'"
        write_status "Warning" "Please install Blender 3.0+ or set BLENDER_PATH environment variable"
        exit 1
    fi

    local version=$("$blender_path" --version 2>&1 | head -1)
    write_status "Success" "Found: $version"
    echo "$blender_path"
}

verify_python() {
    write_status "Info" "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        write_status "Error" "Python 3 not found"
        exit 1
    fi

    local version=$(python3 --version)
    write_status "Success" "Found: $version"
    echo "python3"
}

show_help() {
    cat << 'EOF'

NAR Blender Asset Automation Framework - Unix Launcher
======================================================

USAGE:
    ./run.sh [Mode] [Options]

MODES:
    single      Process a single asset
    batch       Process assets from a directory
    production  Full production workflow with prioritization
    help        Show this help message

EXAMPLES:
    # Process single character
    ./run.sh single --input "path/to/character.blend" \
                    --asset-name "protagonist" \
                    --category character

    # Batch process environment assets
    ./run.sh batch --input "path/to/assets" \
                   --category environment \
                   --threads 4

    # Full production workflow
    ./run.sh production --input "./assets/source" --threads 8

OPTIONS:
    --input         Input file or directory
    --asset-name    Name for the asset
    --category      Asset category (character, environment, prop, weapon, vehicle)
    --config        Configuration file (default: example_config.json)
    --threads       Number of processing threads (default: 4)
    --batch-size    Assets per batch (default: 5)

ENVIRONMENT VARIABLES:
    BLENDER_PATH    Path to Blender executable (auto-detected if not set)

DOCUMENTATION:
    - Quick Start:      src/blender_automation/QUICK_START.md
    - Usage Examples:   src/blender_automation/USAGE_EXAMPLES.md
    - Full Guide:       INSTALL.md

EOF
}

# Parse command-line arguments
shift  # Skip mode
while [[ $# -gt 0 ]]; do
    case $1 in
        --input) INPUT="$2"; shift 2 ;;
        --asset-name) ASSET_NAME="$2"; shift 2 ;;
        --category) CATEGORY="$2"; shift 2 ;;
        --config) CONFIG="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        --batch-size) BATCH_SIZE="$2"; shift 2 ;;
        *) write_status "Warning" "Unknown option: $1"; shift ;;
    esac
done

# Main execution
main() {
    write_status "Info" "Initializing asset pipeline..."
    echo ""

    BLENDER_PATH=$(verify_blender)
    PYTHON_PATH=$(verify_python)

    write_status "Success" "Blender: $BLENDER_PATH"
    write_status "Success" "Python: $PYTHON_PATH"
    echo ""

    if [[ "$MODE" == "help" || -z "$MODE" ]]; then
        show_help
        exit 0
    fi

    # Verify input for non-help modes
    if [[ "$MODE" != "help" && -z "$INPUT" ]]; then
        write_status "Error" "Error: --input parameter required for mode '$MODE'"
        write_status "Info" "Run: ./run.sh help"
        exit 1
    fi

    write_status "Info" "Starting $MODE mode processing..."
    write_status "Info" "Input: $INPUT"
    echo ""

    # Build and execute command
    case $MODE in
        single)
            if [[ -z "$ASSET_NAME" || -z "$CATEGORY" ]]; then
                write_status "Error" "Error: --asset-name and --category required for single mode"
                exit 1
            fi

            cmd="$BLENDER_PATH --background --python src/blender_automation/main.py -- \
                --mode single \
                --input \"$INPUT\" \
                --asset-name \"$ASSET_NAME\" \
                --asset-category \"$CATEGORY\""
            ;;

        batch)
            if [[ -z "$CATEGORY" ]]; then
                write_status "Error" "Error: --category required for batch mode"
                exit 1
            fi

            cmd="$BLENDER_PATH --background --python src/blender_automation/main.py -- \
                --mode batch \
                --input \"$INPUT\" \
                --asset-category \"$CATEGORY\" \
                --threads $THREADS"
            ;;

        production)
            cmd="$PYTHON_PATH src/blender_automation/production_workflow.py \
                --source-dir \"$INPUT\" \
                --threads $THREADS \
                --batch-size $BATCH_SIZE"
            ;;

        *)
            write_status "Error" "Unknown mode: $MODE"
            show_help
            exit 1
            ;;
    esac

    if [[ -n "$CONFIG" ]]; then
        cmd="$cmd --config \"$CONFIG\""
    fi

    write_status "Info" "Executing: $cmd"
    echo ""

    cd "$SCRIPT_DIR"
    eval "$cmd"

    if [[ $? -eq 0 ]]; then
        echo ""
        write_status "Success" "Asset processing completed successfully!"
        write_status "Info" "Check 'exports' directory for output files"
    else
        echo ""
        write_status "Error" "Asset processing failed!"
        exit 1
    fi
}

# Run main function
main "$@"
