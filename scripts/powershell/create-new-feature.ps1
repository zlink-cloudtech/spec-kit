#!/usr/bin/env pwsh
# Create a new feature
[CmdletBinding()]
param(
    [switch]$Json,
    [ValidateSet('feat', 'bug', 'hotfix', 'refactor', 'docs', 'chore')]
    [string]$Type = 'feat',
    [string]$ShortName,
    [int]$Number = 0,
    [string]$SpecDir,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$FeatureDescription
)
$ErrorActionPreference = 'Stop'

# Show help if requested
if ($Help) {
    Write-Host "Usage: ./create-new-feature.ps1 [-Json] [-Type <type>] [-ShortName <name>] [-Number N] [-SpecDir <path>] <feature description>"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Json               Output in JSON format"
    Write-Host "  -Type <type>        Branch type prefix (feat, bug, hotfix, refactor, docs, chore). Default: feat"
    Write-Host "  -ShortName <name>   Provide a custom short name (2-4 words) for the branch"
    Write-Host "  -Number N           Specify branch number manually (overrides auto-detection)"
    Write-Host "  -SpecDir <path>     Use existing directory instead of creating new one"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  ./create-new-feature.ps1 'Add user authentication system' -ShortName 'user-auth'"
    Write-Host "  ./create-new-feature.ps1 -Type bug 'Fix login timeout issue'"
    Write-Host "  ./create-new-feature.ps1 -Type hotfix 'Emergency DB connection fix' -Number 5"
    Write-Host "  ./create-new-feature.ps1 -SpecDir specs/001-oauth-integration 'Add OAuth2 authentication'"
    exit 0
}

# Check if feature description provided
if (-not $FeatureDescription -or $FeatureDescription.Count -eq 0) {
    Write-Error "Usage: ./create-new-feature.ps1 [-Json] [-Type <type>] [-ShortName <name>] <feature description>"
    exit 1
}

$featureDesc = ($FeatureDescription -join ' ').Trim()

# Resolve repository root. Prefer git information when available, but fall back
# to searching for repository markers so the workflow still functions in repositories that
# were initialized with --no-git.
function Find-RepositoryRoot {
    param(
        [string]$StartDir,
        [string[]]$Markers = @('.git', '.specify')
    )
    $current = Resolve-Path $StartDir
    while ($true) {
        foreach ($marker in $Markers) {
            if (Test-Path (Join-Path $current $marker)) {
                return $current
            }
        }
        $parent = Split-Path $current -Parent
        if ($parent -eq $current) {
            # Reached filesystem root without finding markers
            return $null
        }
        $current = $parent
    }
}

function Get-HighestNumberFromSpecs {
    param([string]$SpecsDir)
    
    $highest = 0
    if (Test-Path $SpecsDir) {
        Get-ChildItem -Path $SpecsDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d+)') {
                $num = [int]$matches[1]
                if ($num -gt $highest) { $highest = $num }
            }
        }
    }
    return $highest
}

function Get-HighestNumberFromBranches {
    param()
    
    $highest = 0
    try {
        $branches = git branch -a 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($branch in $branches) {
                # Clean branch name: remove leading markers and remote prefixes
                $cleanBranch = $branch.Trim() -replace '^\*?\s+', '' -replace '^remotes/[^/]+/', ''
                
                # Extract feature number if branch matches pattern type/###-* (new format)
                if ($cleanBranch -match '^(feat|bug|hotfix|refactor|docs|chore)/(\d{3})-') {
                    $num = [int]$matches[2]
                    if ($num -gt $highest) { $highest = $num }
                }
            }
        }
    } catch {
        # If git command fails, return 0
        Write-Verbose "Could not check Git branches: $_"
    }
    return $highest
}

function Get-NextBranchNumber {
    param(
        [string]$SpecsDir
    )

    # Fetch all remotes to get latest branch info (suppress errors if no remotes)
    try {
        git fetch --all --prune 2>$null | Out-Null
    } catch {
        # Ignore fetch errors
    }

    # Get highest number from ALL branches (not just matching short name)
    $highestBranch = Get-HighestNumberFromBranches

    # Get highest number from ALL specs (not just matching short name)
    $highestSpec = Get-HighestNumberFromSpecs -SpecsDir $SpecsDir

    # Take the maximum of both
    $maxNum = [Math]::Max($highestBranch, $highestSpec)

    # Return next number
    return $maxNum + 1
}

function ConvertTo-CleanBranchName {
    param([string]$Name)
    
    return $Name.ToLower() -replace '[^a-z0-9]', '-' -replace '-{2,}', '-' -replace '^-', '' -replace '-$', ''
}

# Function to validate and extract branch name from spec directory
# Returns: @{BranchName="..."; FeatureDir="..."}
function Validate-SpecDir {
    param(
        [string]$SpecDir,
        [string]$RepoRoot
    )
    
    # Resolve absolute path
    if (-not [System.IO.Path]::IsPathRooted($SpecDir)) {
        $SpecDir = Join-Path $RepoRoot $SpecDir
    }
    $SpecDir = [System.IO.Path]::GetFullPath($SpecDir)
    
    # Check if directory exists
    if (-not (Test-Path $SpecDir -PathType Container)) {
        Write-Error "Error: Specified directory does not exist: $SpecDir`nPlease create the directory first or omit -SpecDir to auto-create."
        exit 1
    }
    
    # Extract directory name
    $dirName = Split-Path $SpecDir -Leaf
    
    # Validate directory name format (###-*)
    if ($dirName -notmatch '^\d{3}-') {
        Write-Error "Error: Directory name must match pattern ###-feature-name (e.g., 001-oauth-integration)`nGiven: $dirName"
        exit 1
    }
    
    return @{
        BranchName = $dirName
        FeatureDir = $SpecDir
    }
}

$fallbackRoot = (Find-RepositoryRoot -StartDir $PSScriptRoot)
if (-not $fallbackRoot) {
    Write-Error "Error: Could not determine repository root. Please run this script from within the repository."
    exit 1
}

try {
    $repoRoot = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0) {
        $hasGit = $true
    } else {
        throw "Git not available"
    }
} catch {
    $repoRoot = $fallbackRoot
    $hasGit = $false
}

Set-Location $repoRoot

$specsDir = Join-Path $repoRoot 'specs'
New-Item -ItemType Directory -Path $specsDir -Force | Out-Null

if ($SpecDir) {
    # Mode A: Use existing directory
    Write-Warning "[specify] Using existing directory: $SpecDir"
    
    $result = Validate-SpecDir -SpecDir $SpecDir -RepoRoot $repoRoot
    $specName = $result.BranchName
    $featureDir = $result.FeatureDir
    
    # Build full branch name with type prefix
    $branchName = "$Type/$specName"
    
    # Extract feature number
    if ($specName -match '^(\d{3})') {
        $featureNum = $matches[1]
    } else {
        $featureNum = "000" # Should be caught by validation, but fallback just in case
    }
    
    if ($hasGit) {
        try {
            # Check if branch exists
            git show-ref --verify --quiet "refs/heads/$branchName"
            $localExists = $LASTEXITCODE -eq 0
            
            git show-ref --verify --quiet "refs/remotes/origin/$branchName"
            $remoteExists = $LASTEXITCODE -eq 0
            
            if ($localExists) {
                Write-Warning "[specify] Branch $branchName already exists locally, checking out..."
                git checkout "$branchName" | Out-Null
            } elseif ($remoteExists) {
                Write-Warning "[specify] Branch $branchName exists on remote, checking out..."
                git checkout -b "$branchName" "origin/$branchName" | Out-Null
            } else {
                Write-Warning "[specify] Creating new branch: $branchName"
                git checkout -b "$branchName" | Out-Null
            }
        } catch {
            Write-Warning "Git operation failed: $_"
        }
    } else {
        Write-Warning "[specify] Warning: Git repository not detected; skipped branch operations for $branchName"
    }

} else {
    # Mode B: Auto-create directory (original behavior)

    # Function to generate branch name with stop word filtering and length filtering
    function Get-BranchName {
        param([string]$Description)
        
        # Common stop words to filter out
        $stopWords = @(
            'i', 'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
            'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their',
            'want', 'need', 'add', 'get', 'set'
        )
        
        # Convert to lowercase and extract words (alphanumeric only)
        $cleanName = $Description.ToLower() -replace '[^a-z0-9\s]', ' '
        $words = $cleanName -split '\s+' | Where-Object { $_ }
        
        # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
        $meaningfulWords = @()
        foreach ($word in $words) {
            # Skip stop words
            if ($stopWords -contains $word) { continue }
            
            # Keep words that are length >= 3 OR appear as uppercase in original (likely acronyms)
            if ($word.Length -ge 3) {
                $meaningfulWords += $word
            } elseif ($Description -match "\b$($word.ToUpper())\b") {
                # Keep short words if they appear as uppercase in original (likely acronyms)
                $meaningfulWords += $word
            }
        }
        
        # If we have meaningful words, use first 3-4 of them
        if ($meaningfulWords.Count -gt 0) {
            $maxWords = if ($meaningfulWords.Count -eq 4) { 4 } else { 3 }
            $result = ($meaningfulWords | Select-Object -First $maxWords) -join '-'
            return $result
        } else {
            # Fallback to original logic if no meaningful words found
            $result = ConvertTo-CleanBranchName -Name $Description
            $fallbackWords = ($result -split '-') | Where-Object { $_ } | Select-Object -First 3
            return [string]::Join('-', $fallbackWords)
        }
    }

    # Generate branch name
    if ($ShortName) {
        # Use provided short name, just clean it up
        $branchSuffix = ConvertTo-CleanBranchName -Name $ShortName
    } else {
        # Generate from description with smart filtering
        $branchSuffix = Get-BranchName -Description $featureDesc
    }

    # Determine branch number
    if ($Number -eq 0) {
        if ($hasGit) {
            # Check existing branches on remotes
            $Number = Get-NextBranchNumber -SpecsDir $specsDir
        } else {
            # Fall back to local directory check
            $Number = (Get-HighestNumberFromSpecs -SpecsDir $specsDir) + 1
        }
    }

    $featureNum = ('{0:000}' -f $Number)
    $branchName = "$Type/$featureNum-$branchSuffix"

    # GitHub enforces a 244-byte limit on branch names
    # Validate and truncate if necessary
    $maxBranchLength = 244
    if ($branchName.Length -gt $maxBranchLength) {
        # Calculate how much we need to trim from suffix
        # Account for: type/ (variable) + feature number (3) + hyphen (1)
        $typePrefixLength = $Type.Length + 1
        $maxSuffixLength = $maxBranchLength - $typePrefixLength - 4
        
        # Truncate suffix
        $truncatedSuffix = $branchSuffix.Substring(0, [Math]::Min($branchSuffix.Length, $maxSuffixLength))
        # Remove trailing hyphen if truncation created one
        $truncatedSuffix = $truncatedSuffix -replace '-$', ''
        
        $originalBranchName = $branchName
        $branchName = "$Type/$featureNum-$truncatedSuffix"
        
        Write-Warning "[specify] Branch name exceeded GitHub's 244-byte limit"
        Write-Warning "[specify] Original: $originalBranchName ($($originalBranchName.Length) bytes)"
        Write-Warning "[specify] Truncated to: $branchName ($($branchName.Length) bytes)"
    }

    if ($hasGit) {
        try {
            git checkout -b $branchName | Out-Null
        } catch {
            Write-Warning "Failed to create git branch: $branchName"
        }
    } else {
        Write-Warning "[specify] Warning: Git repository not detected; skipped branch creation for $branchName"
    }

    $featureDir = Join-Path $specsDir "$featureNum-$branchSuffix"
    New-Item -ItemType Directory -Path $featureDir -Force | Out-Null
}

$template = Join-Path $repoRoot '.specify/templates/spec-template.md'
$specFile = Join-Path $featureDir 'spec.md'
if (Test-Path $template) { 
    Copy-Item $template $specFile -Force 
} else { 
    New-Item -ItemType File -Path $specFile | Out-Null 
}

# Set the SPECIFY_FEATURE environment variable for the current session
$env:SPECIFY_FEATURE = $branchName

if ($Json) {
    $obj = [PSCustomObject]@{ 
        BRANCH_NAME = $branchName
        SPEC_FILE = $specFile
        FEATURE_NUM = $featureNum
        BRANCH_TYPE = $Type
        HAS_GIT = $hasGit
    }
    $obj | ConvertTo-Json -Compress
} else {
    Write-Output "BRANCH_NAME: $branchName"
    Write-Output "SPEC_FILE: $specFile"
    Write-Output "FEATURE_NUM: $featureNum"
    Write-Output "BRANCH_TYPE: $Type"
    Write-Output "HAS_GIT: $hasGit"
    Write-Output "SPECIFY_FEATURE environment variable set to: $branchName"
}

