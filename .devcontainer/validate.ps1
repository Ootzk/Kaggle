param()

$ErrorActionPreference = 'Stop'
$repository = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repository
$logDirectory = Join-Path $repository '.git/kaggle-devcontainer'
if (-not (Test-Path -LiteralPath (Join-Path $repository '.git') -PathType Container)) {
    throw 'Run this helper in the main Windows checkout, where .git is a directory.'
}
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$statusPath = Join-Path $logDirectory 'status.txt'

try {
    $codeCommand = (Get-Command code -ErrorAction Stop).Source
    $codeExecutable = Join-Path (Split-Path (Split-Path $codeCommand -Parent) -Parent) 'Code.exe'
    $extension = Get-ChildItem (Join-Path $env:USERPROFILE '.vscode/extensions') -Directory |
        Where-Object Name -Match '^ms-vscode-remote\.remote-containers-\d+\.\d+\.\d+$' |
        Sort-Object { [version]($_.Name -replace '^ms-vscode-remote\.remote-containers-', '') } -Descending |
        Select-Object -First 1
    if (-not $extension) { throw 'Install the VS Code Dev Containers extension first.' }
    $cli = Join-Path $extension.FullName 'dist/spec-node/devContainersSpecCLI.js'
    if (-not (Test-Path -LiteralPath $codeExecutable)) { throw "Missing VS Code runtime: $codeExecutable" }

    'Starting Dev Container (including the image pull). See up.log for progress.' | Set-Content $statusPath
    $previousNodeMode = $env:ELECTRON_RUN_AS_NODE
    try {
        $env:ELECTRON_RUN_AS_NODE = '1'
        $process = Start-Process -FilePath $codeExecutable -WindowStyle Hidden -Wait -PassThru `
            -ArgumentList @(('"' + $cli + '"'), 'up', '--workspace-folder', ('"' + $repository + '"')) `
            -RedirectStandardOutput (Join-Path $logDirectory 'up.json') `
            -RedirectStandardError (Join-Path $logDirectory 'up.log')
    } finally {
        $env:ELECTRON_RUN_AS_NODE = $previousNodeMode
    }
    if ($process.ExitCode -ne 0) { throw "Dev Container startup failed. See $logDirectory/up.log" }
    $result = Get-Content (Join-Path $logDirectory 'up.json') -Raw | ConvertFrom-Json
    if ($result.outcome -ne 'success' -or -not $result.containerId) {
        throw "Unexpected Dev Containers CLI result. See $logDirectory/up.json"
    }

    'Container started; checking imports and CUDA computation.' | Set-Content $statusPath
    $dockerExecutable = (Get-Command docker -ErrorAction Stop).Source
    $check = Start-Process -FilePath $dockerExecutable -WindowStyle Hidden -Wait -PassThru `
        -ArgumentList @('exec', '--workdir', '/workspaces/Kaggle', $result.containerId,
            'python', '.devcontainer/verify_environment.py') `
        -RedirectStandardOutput (Join-Path $logDirectory 'environment.json') `
        -RedirectStandardError (Join-Path $logDirectory 'environment.log')
    if ($check.ExitCode -ne 0) { throw "Environment validation failed. See $logDirectory/environment.log" }
    "Passed: Dev Container startup, repository mount, package imports, CUDA computation. Container: $($result.containerId)" |
        Set-Content $statusPath
    Get-Content $statusPath
} catch {
    ('Failed: ' + $_.Exception.Message) | Set-Content $statusPath
    throw
}
