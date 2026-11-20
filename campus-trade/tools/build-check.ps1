$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Join-Path (Split-Path -Parent $here) 'campus-trade-backend'
$src = Join-Path $root 'src\main\java'
$tmp = Join-Path $env:TEMP 'ctb2'
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null

$files = Get-ChildItem -Path $src -Filter *.java -Recurse
$list = New-Object System.Collections.Generic.List[string]
foreach ($f in $files) {
    $rel = $f.FullName.Substring($src.Length + 1)
    $dest = Join-Path $tmp $rel
    $dir = Split-Path $dest -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $text = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($dest, $text, (New-Object System.Text.UTF8Encoding($false)))
    $list.Add($dest.Replace('\', '/'))
}

$out = Join-Path $tmp 'out'
New-Item -ItemType Directory -Path $out | Out-Null
$jars = (Get-ChildItem -Path 'C:\Users\lxr\.m2\repository' -Filter *.jar -Recurse | ForEach-Object { $_.FullName }) -join ';'
$argfile = Join-Path $tmp 'sources.txt'
[System.IO.File]::WriteAllLines($argfile, $list, [System.Text.Encoding]::ASCII)

Write-Output ("SOURCES=" + $list.Count)
& 'C:\Users\lxr\.jdks\temurin-17.0.20.1\bin\javac.exe' -encoding UTF-8 -nowarn -proc:full -cp $jars -d ($out.Replace('\', '/')) "@$argfile"
Write-Output "EXIT=$LASTEXITCODE"
Write-Output ("CLASS=" + (Get-ChildItem $out -Recurse -Filter *.class | Measure-Object).Count)
