param(
    [Parameter(Mandatory = $true)][string]$DfpDir,
    [Parameter(Mandatory = $true)][string]$Device,
    [Parameter(Mandatory = $true)][string]$TargetPath,
    [Parameter(Mandatory = $true)][string]$ProjectPath,
    [Parameter(Mandatory = $false)][string]$ConfigurationName = "default"
)

$ErrorActionPreference = "Stop"

function Find-JavaExe {
    $appsRoot = Join-Path $env:USERPROFILE ".mplab\app-finder\apps"
    $javaRoot = Join-Path $appsRoot "zulu-fx-jre-8"

    if (Test-Path $javaRoot) {
        $javaCandidates = Get-ChildItem -Path $javaRoot -Filter "java.exe" -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending
        if ($javaCandidates -and $javaCandidates.Count -gt 0) {
            return $javaCandidates[0].FullName
        }
    }

    $fromPath = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($fromPath) {
        return $fromPath.Source
    }

    throw "Unable to locate Java executable. Install MPLAB extensions or Java runtime."
}

function Find-JythonJar {
    $appsRoot = Join-Path $env:USERPROFILE ".mplab\app-finder\apps"
    $backendRoot = Join-Path $appsRoot "mplab_backend"

    if (-not (Test-Path $backendRoot)) {
        throw "MPLAB backend folder not found at $backendRoot"
    }

    $jarCandidates = Get-ChildItem -Path $backendRoot -Filter "mchp-jython-standalone.jar" -Recurse -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending

    if (-not $jarCandidates -or $jarCandidates.Count -eq 0) {
        throw "mchp-jython-standalone.jar not found under $backendRoot"
    }

    return $jarCandidates[0].FullName
}

function Ensure-ChildElement {
    param(
        [xml]$Document,
        [System.Xml.XmlNode]$Parent,
        [string]$Name
    )

    $node = $Parent.SelectSingleNode($Name)
    if (-not $node) {
        $node = $Document.CreateElement($Name)
        $Parent.AppendChild($node) | Out-Null
    }
    return $node
}

function Upsert-ScriptingSetting {
    param(
        [xml]$Document,
        [System.Xml.XmlNode]$ScriptingNode,
        [string]$Key,
        [string]$Value
    )

    $existing = $ScriptingNode.SelectSingleNode("ScriptingSetting[@key='$Key']")
    if ($existing) {
        $existing.SetAttribute("value", $Value)
        return
    }

    $newSetting = $Document.CreateElement("ScriptingSetting")
    $newSetting.SetAttribute("key", $Key)
    $newSetting.SetAttribute("value", $Value)
    $ScriptingNode.AppendChild($newSetting) | Out-Null
}

function New-ConfigXmlSkeleton {
    param(
        [string]$ConfigXmlPath,
        [string]$ConfigurationName,
        [string]$SignedHexPath
    )

    $nbprojectDir = Split-Path -Path $ConfigXmlPath -Parent
    if (-not (Test-Path $nbprojectDir -PathType Container)) {
        New-Item -ItemType Directory -Path $nbprojectDir -Force | Out-Null
    }

    $xmlDoc = New-Object System.Xml.XmlDocument
    $xmlDecl = $xmlDoc.CreateXmlDeclaration("1.0", "UTF-8", $null)
    $xmlDoc.AppendChild($xmlDecl) | Out-Null

    $root = $xmlDoc.CreateElement("configurationDescriptor")
    $xmlDoc.AppendChild($root) | Out-Null

    $confs = $xmlDoc.CreateElement("confs")
    $root.AppendChild($confs) | Out-Null

    $conf = $xmlDoc.CreateElement("conf")
    $conf.SetAttribute("name", $ConfigurationName)
    $confs.AppendChild($conf) | Out-Null

    $scripting = $xmlDoc.CreateElement("ScriptingSettings")
    $conf.AppendChild($scripting) | Out-Null

    $compileType = $xmlDoc.CreateElement("compileType")
    $conf.AppendChild($compileType) | Out-Null

    $loading = $xmlDoc.CreateElement("loading")
    $compileType.AppendChild($loading) | Out-Null

    $useAlternate = $xmlDoc.CreateElement("useAlternateLoadableFile")
    $useAlternate.InnerText = "true"
    $loading.AppendChild($useAlternate) | Out-Null

    $parseOnProd = $xmlDoc.CreateElement("parseOnProdLoad")
    $parseOnProd.InnerText = "true"
    $loading.AppendChild($parseOnProd) | Out-Null

    $alternateFile = $xmlDoc.CreateElement("alternateLoadableFile")
    $alternateFile.InnerText = $SignedHexPath
    $loading.AppendChild($alternateFile) | Out-Null

    $xmlDoc.Save($ConfigXmlPath)
    Write-Host "Created skeleton configurations.xml: $ConfigXmlPath"
}

function Apply-SecureBootSettings {
    param(
        [string]$ConfigXmlPath,
        [string]$SecureBootConfigPath,
        [string]$ConfigurationName,
        [string]$SignedHexPath,
        [string]$WorkspaceRoot,
        [string]$GeneratedProjectDir
    )

    if (-not (Test-Path $ConfigXmlPath -PathType Leaf)) {
        New-ConfigXmlSkeleton -ConfigXmlPath $ConfigXmlPath -ConfigurationName $ConfigurationName -SignedHexPath $SignedHexPath
    }

    if (-not (Test-Path $SecureBootConfigPath -PathType Leaf)) {
        Write-Host "Secure boot config file not found: $SecureBootConfigPath"
        return
    }

    $secureBoot = Get-Content -Path $SecureBootConfigPath -Raw | ConvertFrom-Json

    $xmlDoc = New-Object System.Xml.XmlDocument
    $xmlDoc.PreserveWhitespace = $true
    $xmlDoc.Load($ConfigXmlPath)

    $confNode = $xmlDoc.SelectSingleNode("//conf[@name='$ConfigurationName']")
    if (-not $confNode) {
        $confNode = $xmlDoc.SelectSingleNode("//conf[1]")
    }

    if (-not $confNode) {
        Write-Host "No <conf> node found in $ConfigXmlPath"
        return
    }

    $scriptingNode = $confNode.SelectSingleNode("ScriptingSettings")
    if (-not $scriptingNode) {
        $scriptingNode = $xmlDoc.CreateElement("ScriptingSettings")
        $confNode.AppendChild($scriptingNode) | Out-Null
    }

    $keyFileValue = [string]$secureBoot."configuration.header.key_file"
    if ($keyFileValue.Length -gt 0) {
        $keyFileAbs = $keyFileValue
        if (-not [System.IO.Path]::IsPathRooted($keyFileAbs)) {
            $keyFileAbs = [System.IO.Path]::GetFullPath((Join-Path $WorkspaceRoot $keyFileAbs))
        }

        if (Test-Path $keyFileAbs -PathType Leaf) {
            $projectKeyPath = Join-Path $GeneratedProjectDir ([System.IO.Path]::GetFileName($keyFileAbs))
            if ([System.IO.Path]::GetFullPath($keyFileAbs) -ne [System.IO.Path]::GetFullPath($projectKeyPath)) {
                Copy-Item -Path $keyFileAbs -Destination $projectKeyPath -Force
            }
            $keyFileValue = [System.IO.Path]::GetFileName($projectKeyPath)
        } else {
            Write-Host "Configured key file not found: $keyFileAbs"
        }
    }

    $settingsMap = @{
        "configuration.header.flash_type" = [string]$secureBoot."configuration.header.flash_type"
        "configuration.header.auth"       = [string]$secureBoot."configuration.header.auth"
        "configuration.header.fw_rev"     = [string]$secureBoot."configuration.header.fw_rev"
        "configuration.header.sequence"   = [string]$secureBoot."configuration.header.sequence"
        "configuration.header.ecdsa_mthd" = [string]$secureBoot."configuration.header.ecdsa_mthd"
        "configuration.header.key_file"   = $keyFileValue
    }

    foreach ($key in $settingsMap.Keys) {
        $value = $settingsMap[$key]
        if ($null -eq $value) {
            $value = ""
        }
        Upsert-ScriptingSetting -Document $xmlDoc -ScriptingNode $scriptingNode -Key $key -Value $value
    }

    $compileType = Ensure-ChildElement -Document $xmlDoc -Parent $confNode -Name "compileType"
    $loading = Ensure-ChildElement -Document $xmlDoc -Parent $compileType -Name "loading"

    $useAlternate = Ensure-ChildElement -Document $xmlDoc -Parent $loading -Name "useAlternateLoadableFile"
    $parseOnProd = Ensure-ChildElement -Document $xmlDoc -Parent $loading -Name "parseOnProdLoad"
    $alternateFile = Ensure-ChildElement -Document $xmlDoc -Parent $loading -Name "alternateLoadableFile"

    $useAlternate.InnerText = "true"
    $parseOnProd.InnerText = "true"
    $alternateFile.InnerText = $SignedHexPath

    $xmlDoc.Save($ConfigXmlPath)
    Write-Host "Updated secure boot settings in $ConfigXmlPath"
}

$targetDir = Split-Path -Path $TargetPath -Parent
$targetName = [System.IO.Path]::GetFileNameWithoutExtension($TargetPath)
$hexPath = Join-Path $targetDir ($targetName + ".hex")
$signedHexPath = Join-Path $targetDir ($targetName + ".signed.hex")
$projectXPath = Join-Path $targetDir ($targetName + ".X")

if (-not (Test-Path $projectXPath -PathType Container)) {
    New-Item -ItemType Directory -Path $projectXPath -Force | Out-Null
}

$configXmlPath = Join-Path $projectXPath "nbproject\configurations.xml"
$secureBootConfigPath = Join-Path $ProjectPath ".vscode\secureboot.config.json"

Apply-SecureBootSettings -ConfigXmlPath $configXmlPath -SecureBootConfigPath $secureBootConfigPath -ConfigurationName $ConfigurationName -SignedHexPath $signedHexPath -WorkspaceRoot $ProjectPath -GeneratedProjectDir $projectXPath

$javaExe = Find-JavaExe
$jythonJar = Find-JythonJar

$signScript = Join-Path $DfpDir "$Device\scripts\sign.py"
if (-not (Test-Path $signScript -PathType Leaf)) {
    $signScript = Join-Path $DfpDir "scripts\sign.py"
}
if (-not (Test-Path $signScript -PathType Leaf)) {
    $found = Get-ChildItem -Path $DfpDir -Filter "sign.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $signScript = $found.FullName }
}
if (-not (Test-Path $signScript -PathType Leaf)) {
    throw "Unable to find sign.py under $DfpDir"
}

$propertiesScript = Join-Path $DfpDir "$Device\scripts\properties_device.py"
if (-not (Test-Path $propertiesScript -PathType Leaf)) {
    $propertiesScript = Join-Path $DfpDir "scripts\properties_device.py"
}
if (-not (Test-Path $propertiesScript -PathType Leaf)) {
    $found = Get-ChildItem -Path $DfpDir -Filter "properties_device.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $propertiesScript = $found.FullName }
}
if (-not (Test-Path $propertiesScript -PathType Leaf)) {
    throw "Unable to find properties_device.py under $DfpDir"
}

if (-not (Test-Path $hexPath -PathType Leaf)) {
    throw "Hex file not found: $hexPath"
}

& $javaExe -jar $jythonJar $signScript $propertiesScript $hexPath $projectXPath $ConfigurationName on_project_load_done None
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if (-not (Test-Path $signedHexPath -PathType Leaf)) {
    throw "Signing step completed without creating signed hex: $signedHexPath"
}

Write-Host "Signed image generated: $signedHexPath"
