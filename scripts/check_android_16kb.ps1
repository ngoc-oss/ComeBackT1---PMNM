# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
param(
    [Parameter(Mandatory = $false)]
    [string]$Apk = "android/app/build/outputs/apk/debug/app-universal-debug.apk"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$apkPath = Join-Path $root $Apk
if (-not (Test-Path $apkPath)) { throw "APK not found: $apkPath" }
if (-not $env:ANDROID_HOME) { throw "ANDROID_HOME is not set." }
$zipalign = Get-ChildItem (Join-Path $env:ANDROID_HOME "build-tools") -Recurse -Filter zipalign.exe |
    Sort-Object FullName -Descending | Select-Object -First 1
if (-not $zipalign) { throw "zipalign.exe not found. Install Android SDK Build-Tools 35+." }
& $zipalign.FullName -c -P 16 -v 4 $apkPath
if ($LASTEXITCODE -ne 0) { throw "16 KB ZIP alignment check failed." }
Write-Host "16 KB ZIP alignment: PASS"
Write-Host "Also inspect every native .so Alignment column with Android Studio: Build > Analyze APK."
