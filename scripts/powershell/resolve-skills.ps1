#!/usr/bin/env pwsh
# resolve-skills.ps1 v2.0.0 — Phase-based skill resolver (PowerShell, no Python required)
# Usage: pwsh scripts/powershell/resolve-skills.ps1 <phase> [repo_root]
#        pwsh scripts/powershell/resolve-skills.ps1 --list-domain [repo_root]

param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$Phase,

    [Parameter(Position = 1, Mandatory = $false)]
    [string]$RepoRoot = $PWD
)

$SCRIPT_VERSION = "2.0.0"
$DEFAULT_SKILL_DIRS = @("skills", ".specify/skills", ".github/skills", ".claude/skills")

# ─── Utilities ───────────────────────────────────────────────────────────────

function Unquote([string]$s) {
    if ($s.Length -ge 2) {
        if (($s[0] -eq '"' -and $s[-1] -eq '"') -or ($s[0] -eq "'" -and $s[-1] -eq "'")) {
            return $s.Substring(1, $s.Length - 2)
        }
    }
    return $s
}

# ─── Config ──────────────────────────────────────────────────────────────────

function Get-SkillDirs([string]$Root) {
    $configPath = Join-Path $Root ".speckit.yaml"

    if (-not (Test-Path $configPath -PathType Leaf)) {
        return $DEFAULT_SKILL_DIRS | ForEach-Object { Join-Path $Root $_ }
    }

    $scanDirs = @()
    $inSkills = $false
    $inScanDirs = $false
    $cfgVersion = ""

    foreach ($line in [System.IO.File]::ReadAllLines($configPath)) {
        $stripped = $line.Trim()
        if ($stripped -eq "" -or $stripped.StartsWith("#")) { continue }

        $isTopLevel = ($line.Length -gt 0 -and $line[0] -ne ' ' -and $line[0] -ne "`t")

        if ($isTopLevel) {
            $inSkills = $false
            $inScanDirs = $false
            if ($stripped -match '^version:\s*(.+)$') {
                $cfgVersion = Unquote $matches[1].Trim()
            } elseif ($stripped -eq "skills:") {
                $inSkills = $true
            }
        } elseif ($inSkills) {
            if ($stripped -eq "scan_dirs:") {
                $inScanDirs = $true
            } elseif ($inScanDirs -and $stripped -match '^-\s+(.+)$') {
                $scanDirs += $matches[1].Trim().TrimEnd('/', '\')
            } elseif ($stripped -ne "scan_dirs:" -and $stripped -notmatch '^-\s+') {
                $inScanDirs = $false
            }
        }
    }

    if ($cfgVersion -ne "") {
        $scriptMajor = $SCRIPT_VERSION.Split('.')[0]
        $cfgMajor = $cfgVersion.Split('.')[0]
        if ($cfgMajor -ne "" -and $cfgMajor -ne $scriptMajor) {
            [Console]::Error.WriteLine(
                "Warning: .speckit.yaml version $cfgVersion may be incompatible with resolve-skills.ps1 $SCRIPT_VERSION"
            )
        }
    }

    if ($scanDirs.Count -gt 0) {
        return $scanDirs | ForEach-Object { Join-Path $Root $_ }
    }

    return $DEFAULT_SKILL_DIRS | ForEach-Object { Join-Path $Root $_ }
}

# ─── SKILL.md Parser ─────────────────────────────────────────────────────────
# Returns [PSCustomObject]@{ Name; Desc }

function Parse-SkillMd([string]$Path, [string]$Fallback) {
    $result = [PSCustomObject]@{ Name = $Fallback; Desc = "" }

    if (-not (Test-Path $Path -PathType Leaf)) { return $result }

    $allLines = [System.IO.File]::ReadAllLines($Path)
    if ($allLines.Count -eq 0 -or $allLines[0] -ne "---") { return $result }

    # Find closing ---
    $fmEnd = -1
    for ($i = 1; $i -lt $allLines.Count; $i++) {
        if ($allLines[$i] -eq "---") { $fmEnd = $i; break }
    }
    if ($fmEnd -lt 0) { return $result }

    $inBlock = $false
    $blockLines = [System.Collections.Generic.List[string]]::new()

    for ($i = 1; $i -lt $fmEnd; $i++) {
        $line = $allLines[$i]

        if ($inBlock) {
            if ($line.Length -gt 0 -and $line[0] -ne ' ' -and $line[0] -ne "`t") {
                # Block ended
                $inBlock = $false
                if ($blockLines.Count -gt 0) {
                    $result.Desc = [string]::Join(" ", $blockLines)
                }
                $blockLines.Clear()
                # Re-process this line
                $stripped = $line.Trim()
                if ($stripped -match '^name:\s*(.*)$') {
                    $val = Unquote $matches[1].Trim()
                    if ($val -ne "") { $result.Name = $val }
                }
            } else {
                $content = $line.Trim()
                if ($content -ne "") { $blockLines.Add($content) | Out-Null }
            }
            continue
        }

        $stripped = $line.Trim()

        if ($stripped -match '^name:\s*(.*)$') {
            $val = Unquote $matches[1].Trim()
            if ($val -ne "") { $result.Name = $val }
        } elseif ($stripped -match '^description:\s*(.*)$') {
            $val = $matches[1].Trim()
            if ($val -in @("|", ">", ">-", "|-")) {
                $inBlock = $true
                $blockLines.Clear()
            } else {
                $result.Desc = Unquote $val
            }
        }
    }

    if ($inBlock -and $blockLines.Count -gt 0) {
        $result.Desc = [string]::Join(" ", $blockLines)
    }

    return $result
}

# ─── Adapter YAML Parser ─────────────────────────────────────────────────────
# Returns list of matched skill objects sorted externally

function Load-AdapterSkills([string]$AdapterFile, [string]$Phase) {
    $skillDir = Split-Path $AdapterFile -Parent
    $adapterName = "Unknown"
    $inHooks = $false
    $hasHook = $false
    $hookPhase = ""
    $hookPriority = 0
    $hookContext = ""
    $hookInstructions = ""
    $inInstructions = $false
    $instrIndent = 0
    $instrLines = [System.Collections.Generic.List[string]]::new()
    $results = [System.Collections.Generic.List[object]]::new()

    $flushHook = {
        if ($hasHook -and $hookPhase -eq $Phase -and $hookContext -ne "") {
            $ctx = Join-Path $skillDir $hookContext
            if (Test-Path $ctx -PathType Leaf) {
                $sm = Parse-SkillMd $ctx $adapterName
                $results.Add([PSCustomObject]@{
                    Priority     = $hookPriority
                    Path         = $ctx
                    Name         = $sm.Name
                    Desc         = $sm.Desc
                    Instructions = $hookInstructions
                }) | Out-Null
            }
        }
        $hasHook = $false
        $hookPhase = ""
        $hookPriority = 0
        $hookContext = ""
        $hookInstructions = ""
        $inInstructions = $false
        $instrIndent = 0
        $instrLines.Clear()
    }

    foreach ($rawLine in [System.IO.File]::ReadAllLines($AdapterFile)) {
        $line = $rawLine.TrimEnd("`r")

        # ── Open instructions block ──────────────────────────────────────────
        if ($inInstructions) {
            $strippedL = $line.Trim()
            $isNonIndented = ($line.Length -gt 0 -and $line[0] -ne ' ' -and $line[0] -ne "`t")
            $isNewHook = $strippedL -match '^-\s+phase:'

            if ($isNonIndented -or $isNewHook) {
                # End instructions block
                if ($instrLines.Count -gt 0) {
                    $hookInstructions = [string]::Join("`n", $instrLines)
                }
                $inInstructions = $false
                $instrIndent = 0
                $instrLines.Clear()
                # Fall through and re-process this line
            } else {
                if ($instrIndent -eq 0 -and $strippedL -ne "") {
                    $instrIndent = $line.Length - $line.TrimStart().Length
                }
                if ($instrIndent -gt 0 -and $line.Length -ge $instrIndent) {
                    $instrLines.Add($line.Substring($instrIndent)) | Out-Null
                } else {
                    $instrLines.Add($strippedL) | Out-Null
                }
                continue
            }
        }

        $stripped = $line.Trim()
        if ($stripped -eq "") { continue }

        $isTopLevel = ($line.Length -gt 0 -and $line[0] -ne ' ' -and $line[0] -ne "`t")

        if ($isTopLevel) {
            $inHooks = $false
            if ($stripped -match '^name:\s*(.+)$') {
                $adapterName = $matches[1].Trim()
            } elseif ($stripped -eq "hooks:") {
                $inHooks = $true
            }
        } elseif ($inHooks) {
            if ($stripped -match '^-\s+phase:\s*(.+)$') {
                & $flushHook
                $hasHook = $true
                $hookPhase = $matches[1].Trim()
            } elseif ($hasHook) {
                if ($stripped -match '^priority:\s*(.+)$') {
                    $hookPriority = [int]$matches[1].Trim()
                } elseif ($stripped -match '^context:\s*(.+)$') {
                    $hookContext = $matches[1].Trim()
                } elseif ($stripped -match '^instructions:\s*(.*)$') {
                    $val = $matches[1].Trim()
                    if ($val -eq "|" -or $val -eq ">") {
                        $inInstructions = $true
                        $instrIndent = 0
                        $instrLines.Clear()
                    } else {
                        $hookInstructions = $val
                    }
                }
            }
        }
    }

    # Flush any trailing open instructions block
    if ($inInstructions -and $instrLines.Count -gt 0) {
        $hookInstructions = [string]::Join("`n", $instrLines)
    }

    & $flushHook

    return $results
}

# ─── Commands ────────────────────────────────────────────────────────────────

function Invoke-ListDomain([string]$Root) {
    $skillDirs = Get-SkillDirs $Root
    $found = $false
    $seenNames = @{}

    foreach ($skillsDir in $skillDirs) {
        if (-not (Test-Path $skillsDir -PathType Container)) { continue }

        Get-ChildItem -Path $skillsDir -Directory | Sort-Object Name | ForEach-Object {
            $skillPath = $_.FullName
            $skillMd   = Join-Path $skillPath "SKILL.md"
            $adapter   = Join-Path $skillPath "speckit-adapter.yaml"

            if (-not (Test-Path $skillMd -PathType Leaf)) { return }
            if (Test-Path $adapter -PathType Leaf) { return }  # skip adapter-backed skills

            $sm = Parse-SkillMd $skillMd $_.Name
            if (-not $seenNames.ContainsKey($sm.Name)) {
                $seenNames[$sm.Name] = $true
                $desc = if ($sm.Desc -ne "") { $sm.Desc } else { "(no description)" }
                Write-Output "- **$($sm.Name)**: $desc"
                $found = $true
            }
        }
    }

    if (-not $found) {
        Write-Output "_No domain skills found in configured scan directories._"
    }
}

function Invoke-Phase([string]$Phase, [string]$Root) {
    $skillDirs = Get-SkillDirs $Root
    $allSkills = [System.Collections.Generic.List[object]]::new()

    foreach ($skillsDir in $skillDirs) {
        if (-not (Test-Path $skillsDir -PathType Container)) { continue }

        Get-ChildItem -Path $skillsDir -Directory | ForEach-Object {
            $adapterFile = Join-Path $_.FullName "speckit-adapter.yaml"
            if (Test-Path $adapterFile -PathType Leaf) {
                $matched = Load-AdapterSkills $adapterFile $Phase
                foreach ($s in $matched) { $allSkills.Add($s) | Out-Null }
            }
        }
    }

    $count = $allSkills.Count

    if ($count -eq 0) {
        Write-Output "<active_skills phase=""$Phase"" count=""0"">"
        Write-Output "  <directive>No specialist skills are configured for this phase. Proceed with general best practices.</directive>"
        Write-Output "</active_skills>"
        return
    }

    $sorted = $allSkills | Sort-Object Priority -Descending

    Write-Output "<active_skills phase=""$Phase"" count=""$count"">"
    Write-Output "  <directive>The following specialist skills are active for this phase. You MUST read each skill's persona_file and fully adopt its persona and workflows before proceeding.</directive>"

    foreach ($skill in $sorted) {
        Write-Output ""
        Write-Output "  <skill name=""$($skill.Name)"">"
        if ($skill.Desc -ne "") {
            Write-Output "    <description>$($skill.Desc)</description>"
        }
        Write-Output "    <persona_file>$($skill.Path)</persona_file>"
        if ($skill.Instructions -ne "") {
            Write-Output "    <integration>"
            Write-Output $skill.Instructions
            Write-Output "    </integration>"
        }
        Write-Output "  </skill>"
    }

    Write-Output ""
    Write-Output "</active_skills>"
}

# ─── Entry Point ─────────────────────────────────────────────────────────────

if ($Phase -eq "--list-domain") {
    Invoke-ListDomain $RepoRoot
} else {
    Invoke-Phase $Phase $RepoRoot
}
