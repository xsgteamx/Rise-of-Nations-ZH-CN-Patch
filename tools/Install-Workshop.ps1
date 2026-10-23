# Creates/removes only a directory junction. Never copies game data or changes settings.
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)][string]$GamePath,
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
if (Get-Process riseofnations,patriots -ErrorAction SilentlyContinue) {
    throw 'Close Rise of Nations and its launcher first.'
}
$game = (Resolve-Path -LiteralPath $GamePath).Path.TrimEnd('\')
if (-not (Test-Path -LiteralPath (Join-Path $game 'riseofnations.exe') -PathType Leaf)) {
    throw 'GamePath must be the Rise of Nations installation folder.'
}
$steamapps = Split-Path (Split-Path $game -Parent) -Parent
if ((Split-Path $steamapps -Leaf) -ne 'steamapps') { throw 'Expected steamapps/common/game layout.' }
$target = Join-Path $steamapps 'workshop\content\287450\3824946614'
$mods = Join-Path $game 'mods'
$link = Join-Path $mods 'RON_zhCN_Compatibility'
$existing = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
if ($existing) {
    if ($existing.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath([string]@($existing.Target)[0]).TrimEnd('\') -ne $target) {
        throw 'Local path already exists and is not our junction. Back it up separately; nothing was changed.'
    }
    if ($Remove) {
        if ($PSCmdlet.ShouldProcess($link, 'Remove junction only (keep Steam download)')) {
            [IO.Directory]::Delete($link, $false)
        }
        Write-Output 'Junction removed. Disable the subscribed mod or unsubscribe in Steam, then restart the game.'
    } else { Write-Output 'Already installed. Steam updates the linked files.' }
    return
}
if ($Remove) { Write-Output 'No junction to remove.'; return }
foreach ($required in @('Data\fonts.xml','Data\NotoSansCJKsc-Regular.otf','Data\NotoSansCJKsc-Bold.otf','OFL.txt','SOURCES.txt')) {
    if (-not (Test-Path -LiteralPath (Join-Path $target $required) -PathType Leaf)) {
        throw "Subscribe to item 3824946614 and let Steam finish downloading first. Missing: $required"
    }
}
# Reject truncated fonts before changing anything. These unmodified OFL fonts are pinned.
$hashes = @{
    'NotoSansCJKsc-Regular.otf' = '2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b'
    'NotoSansCJKsc-Bold.otf' = 'b5f0d1a190a7f9b43c310a8850630af12553df32c4c050543f9059732d9b4c0a'
}
foreach ($font in $hashes.Keys) {
    if ((Get-FileHash -LiteralPath (Join-Path $target "Data\$font") -Algorithm SHA256).Hash -ne $hashes[$font]) {
        throw "Font integrity check failed: $font"
    }
}
if ($PSCmdlet.ShouldProcess($link, "Create junction to $target")) {
    if (-not (Test-Path -LiteralPath $mods)) { New-Item -ItemType Directory -Path $mods | Out-Null }
    New-Item -ItemType Junction -Path $link -Target $target | Out-Null
}
Write-Output 'Installed. Launch through Steam. Keep the LOCAL entry enabled; restart after changing mod state.'
