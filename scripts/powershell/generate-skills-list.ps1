<#
.SYNOPSIS
    Generates an XML list of available skills and injects them into a template.

.DESCRIPTION
    Scans the provided paths for SKILL.md files, extracts their name and description 
    from YAML frontmatter, and injects the XML into the provided template file.

.PARAMETER Path
    Path(s) to directories containing skills.

.PARAMETER Output
    File path to save the generated content.

.PARAMETER Template
    Template file path (default: .specify/templates/instructions/speckit-skills.instructions.md)

.PARAMETER Force
    Overwrite the output file if it exists.

.PARAMETER Help
    Show usage information.

.EXAMPLE
    .\scripts\powershell\generate-skills-list.ps1 -p skills/
#>

param(
    [Parameter(Mandatory=$true)]
    [Alias("p")]
    [string[]]$Path,

    [Alias("o")]
    [string]$Output,

    [Alias("t")]
    [string]$Template = ".specify/templates/instructions/speckit-skills.instructions.md",

    [Alias("f")]
    [switch]$Force,

    [Alias("h")]
    [switch]$Help
)

if ($Help) {
    Get-Help $PSCommandPath
    exit 0
}

if ($Output) {
    $outDir = Split-Path $Output -Parent
    if ([string]::IsNullOrEmpty($outDir)) { $outDir = "." }
    if (-not (Test-Path $outDir)) {
        Write-Error "Error: Output directory '$outDir' does not exist."
        exit 1
    }
    
    if ((Test-Path $Output) -and (-not $Force)) {
        Write-Error "Output file '$Output' already exists. Use -Force to overwrite."
        exit 1
    }

    # Basic write permission check on existing file
    if (Test-Path $Output) {
        try {
            [IO.File]::OpenWrite($Output).Close()
        } catch {
            Write-Error "Error: Cannot write to output file '$Output'. Access denied."
            exit 1
        }
    }
}

function Get-SkillFromMd {
    param([string]$FilePath)
    
    $content = Get-Content -Path $FilePath -Raw
    $name = ""
    $description = ""
    
    # Simple regex to extract frontmatter fields
    if ($content -match '(?s)^---(.*?)---') {
        $frontmatter = $Matches[1]
        if ($frontmatter -match 'name:\s*(.*)') {
            $name = $Matches[1].Trim()
        }
        if ($frontmatter -match 'description:\s*(.*)') {
            $description = $Matches[1].Trim()
        }
    }
    
    if ($name -and $description) {
        return @{
            Name = $name
            Description = $description
            Location = $FilePath
        }
    }
    return $null
}

$xml = New-Object System.Collections.Generic.List[string]
$xml.Add("<available_skills>")

foreach ($dir in $Path) {
    if (-not (Test-Path $dir -PathType Container)) {
        Write-Warning "Path '$dir' is not a directory. Skipping."
        continue
    }

    try {
        $skillFiles = Get-ChildItem -Path $dir -Filter "SKILL.md" -Recurse -ErrorAction Stop
    } catch {
        Write-Error "Error: Cannot read directory '$dir': $($_.Exception.Message)"
        exit 1
    }

    foreach ($file in $skillFiles) {
        $skill = Get-SkillFromMd -FilePath $file.FullName
        if ($skill) {
            # Normalize path to use forward slashes and make it relative to current directory if possible
            $relativePath = $file.FullName
            $currentDir = Get-Location
            if ($relativePath.StartsWith($currentDir)) {
                $relativePath = $relativePath.Substring($currentDir.Path.Length + 1).Replace('\', '/')
            }
            # Remove leading ./ or .\ if present
            $relativePath = $relativePath -replace '^\.\\', '' -replace '^\./', ''

            $xml.Add("  <skill>")
            $xml.Add("    <name>$($skill.Name)</name>")
            $xml.Add("    <description>$($skill.Description)</description>")
            $xml.Add("    <location>`${workspaceFolder}/$relativePath</location>")
            $xml.Add("  </skill>")
        }
    }
}

$xml.Add("</available_skills>")
$xmlContent = $xml -join "`n"

$finalContent = $xmlContent

if (Test-Path $Template) {
    $templateContent = Get-Content -Path $Template -Raw
    # Replace placeholder with XML content
    $finalContent = $templateContent.Replace("{SKILLS_LIST}", $xmlContent)
} else {
    Write-Warning "Template file '$Template' not found. Outputting raw XML."
}

if ($Output) {
    if ((Test-Path $Output) -and (-not $Force)) {
        Write-Error "Output file '$Output' already exists. Use -Force to overwrite."
        exit 1
    }
    Set-Content -Path $Output -Value $finalContent -Force:$Force
    Write-Host "Generated skills list saved to $Output"
} else {
    Write-Output $finalContent
}
