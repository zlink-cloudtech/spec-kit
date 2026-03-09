#!/usr/bin/env pwsh
# setup-uml-dir.ps1 — Initialize the uml/ subdirectory inside a feature directory.
#
# Usage:
#   ./setup-uml-dir.ps1 [-FeatureDir <path>]
#   $env:FEATURE_DIR = '/path/to/feature'; ./setup-uml-dir.ps1
#
# Priority: -FeatureDir param > $env:FEATURE_DIR
# Output:   absolute path to the created uml/ directory (stdout)
# Exit 0:   success (idempotent)
# Exit 1:   no feature directory specified

[CmdletBinding()]
param(
    [string]$FeatureDir = ""
)

$ErrorActionPreference = 'Stop'

# Resolve feature directory: param takes precedence over env var
if ($FeatureDir) {
    $targetDir = $FeatureDir
} elseif ($env:FEATURE_DIR) {
    $targetDir = $env:FEATURE_DIR
} else {
    Write-Error "No feature directory specified. Pass -FeatureDir or set FEATURE_DIR env var."
    exit 1
}

# Resolve to absolute path
$targetDir = (Resolve-Path $targetDir).Path

# Create the uml/ subdirectory (idempotent)
$umlDir = Join-Path $targetDir "uml"
New-Item -ItemType Directory -Path $umlDir -Force | Out-Null

# Output the absolute path
Write-Output $umlDir
