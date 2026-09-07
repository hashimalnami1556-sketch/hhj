# NAR Blender Asset Automation Framework - Windows Launch Script
# PowerShell script for easy asset processing on Windows

param(
    [Parameter(Position = 0)]
    [ValidateSet("single", "batch", "production", "help")]
    [string]$Mode = "help",

    [Parameter()]
    [string]$Input,

    [Parameter()]
    [string]$AssetName,

    [Parameter()]
    [ValidateSet("character", "environment", "prop", "weapon", "vehicle")]
    [string]$Category,

    [Parameter()]
    [string]$Config,

    [Parameter()]
    [int]$Threads = 4,

    [Parameter()]
    [int]$BatchSize = 5
)

$ErrorActionPreference = "Stop"

# Colors for output
$colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

function Write-Status {
    param($Message, $Status = "Info")
    Write-Host "[$Status] " -ForegroundColor $colors[$Status] -NoNewline
    Write-Host $Message
}

function Verify-Blender {
    Write-Status "Checking Blender installation..." Info

    $blenderPath = if ($env:BLENDER_PATH) {
        $env:BLENDER_PATH
    } else {
        "blender"
    }

    try {
        $version = & $blenderPath --version 2>&1
        Write-Status "Found: $version" Success
        return $blenderPath
    } catch {
        Write-Status "Blender not found at '$blenderPath'" Error
        Write-Status "Please install Blender 3.0+ or set BLENDER_PATH environment variable" Warning
        exit 1
    }
}

function Verify-Python {
    Write-Status "Checking Python installation..." Info

    try {
        $version = python --version 2>&1
        Write-Status "Found: $version" Success
        return "python"
    } catch {
        Write-Status "Python not found" Error
        exit 1
    }
}

function Show-Help {
    Write-Host @"
NAR Blender Asset Automation Framework - Windows Launcher
=========================================================

USAGE:
    ./run.ps1 [Mode] [Options]

MODES:
    single      Process a single asset
    batch       Process assets from a directory
    production  Full production workflow with prioritization
    help        Show this help message

EXAMPLES:
    # Process single character
    ./run.ps1 single -Input "path\to\character.blend" -AssetName "protagonist" -Category character

    # Batch process environment assets
    ./run.ps1 batch -Input "path\to\assets" -Category environment -Threads 4

    # Full production workflow
    ./run.ps1 production -Input ".\assets\source" -Threads 8

OPTIONS:
    -Input          Input file or directory
    -AssetName      Name for the asset
    -Category       Asset category (character, environment, prop, weapon, vehicle)
    -Config         Configuration file (default: example_config.json)
    -Threads        Number of processing threads (default: 4)
    -BatchSize      Assets per batch (default: 5)

ENVIRONMENT VARIABLES:
    BLENDER_PATH    Path to Blender executable (auto-detected if not set)

DOCUMENTATION:
    - Quick Start:      src\blender_automation\QUICK_START.md
    - Usage Examples:   src\blender_automation\USAGE_EXAMPLES.md
    - Full Guide:       INSTALL.md

"@
}

# Main script
try {
    # Verify prerequisites
    Write-Status "Initializing asset pipeline..." Info
    Write-Host ""

    $blenderPath = Verify-Blender
    $pythonPath = Verify-Python

    Write-Status "Blender: $blenderPath" Success
    Write-Status "Python: $pythonPath" Success
    Write-Host ""

    if ($Mode -eq "help" -or $Mode -eq "") {
        Show-Help
        exit 0
    }

    # Verify input
    if ($Mode -ne "help" -and -not $Input) {
        Write-Status "Error: -Input parameter required for mode '$Mode'" Error
        Write-Status "Run: ./run.ps1 help" Info
        exit 1
    }

    Write-Status "Starting $Mode mode processing..." Info
    Write-Status "Input: $Input" Info

    # Build command based on mode
    $cmd = @()

    if ($Mode -eq "single") {
        if (-not $AssetName -or -not $Category) {
            Write-Status "Error: -AssetName and -Category required for single mode" Error
            exit 1
        }

        $cmd = @(
            $blenderPath, "--background", "--python", "src\blender_automation\main.py", "--",
            "--mode", "single",
            "--input", $Input,
            "--asset-name", $AssetName,
            "--asset-category", $Category
        )
    }

    elseif ($Mode -eq "batch") {
        if (-not $Category) {
            Write-Status "Error: -Category required for batch mode" Error
            exit 1
        }

        $cmd = @(
            $blenderPath, "--background", "--python", "src\blender_automation\main.py", "--",
            "--mode", "batch",
            "--input", $Input,
            "--asset-category", $Category,
            "--threads", $Threads.ToString()
        )
    }

    elseif ($Mode -eq "production") {
        $cmd = @(
            $pythonPath, "src\blender_automation\production_workflow.py",
            "--source-dir", $Input,
            "--threads", $Threads.ToString(),
            "--batch-size", $BatchSize.ToString()
        )
    }

    if ($Config) {
        $cmd += @("--config", $Config)
    }

    # Execute command
    Write-Host ""
    Write-Status "Executing: $($cmd -join ' ')" Info
    Write-Host ""

    & $cmd

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Status "Asset processing completed successfully!" Success
        Write-Status "Check 'exports' directory for output files" Info
    } else {
        Write-Host ""
        Write-Status "Asset processing failed with exit code $LASTEXITCODE" Error
        exit $LASTEXITCODE
    }

} catch {
    Write-Status "Error: $_" Error
    exit 1
}
