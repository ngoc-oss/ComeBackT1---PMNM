# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
param([switch]$SkipDeviceTests, [switch]$Skip16KbCheck)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$androidRoot = Join-Path $projectRoot "android"
$releaseRoot = Join-Path $projectRoot "releases"
New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null

& python (Join-Path $PSScriptRoot "verify_release.py")
if ($LASTEXITCODE -ne 0) { throw "Source release audit failed." }

Push-Location $androidRoot
try {
    & .\gradlew.bat --version
    & .\gradlew.bat clean :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
    if ($LASTEXITCODE -ne 0) { throw "Gradle verification/build failed." }
    if (-not $SkipDeviceTests) {
        $adb = Get-Command adb -ErrorAction SilentlyContinue
        $devices = if ($adb) { (& adb devices) | Select-String "\tdevice$" } else { $null }
        if ($devices) {
            & .\gradlew.bat :app:connectedDebugAndroidTest
            if ($LASTEXITCODE -ne 0) { throw "Android instrumentation tests failed." }
        } else {
            Write-Warning "No online emulator/USB device; instrumentation tests were not run."
        }
    }
    $outputRoot = Join-Path $androidRoot "app\build\outputs\apk\debug"
    $copies = @{
        "app-armeabi-v7a-debug.apk" = "FreshCheck-0.5.1-armeabi-v7a.apk"
        "app-arm64-v8a-debug.apk" = "FreshCheck-0.5.1-arm64-v8a.apk"
        "app-x86_64-debug.apk" = "FreshCheck-0.5.1-x86_64.apk"
        "app-universal-debug.apk" = "FreshCheck-0.5.1-universal.apk"
    }
    foreach ($sourceName in $copies.Keys) {
        Copy-Item -Force (Join-Path $outputRoot $sourceName) (Join-Path $releaseRoot $copies[$sourceName])
    }
} finally { Pop-Location }

if (-not $Skip16KbCheck) {
    & (Join-Path $PSScriptRoot "check_android_16kb.ps1") -Apk "releases/FreshCheck-0.5.1-universal.apk"
}
Get-FileHash (Join-Path $releaseRoot "*.apk") -Algorithm SHA256 |
    Format-Table -AutoSize
