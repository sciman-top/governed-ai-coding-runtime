# Windows Process Environment Recovery

## Symptom

In Codex, CI wrappers, or reduced PowerShell sessions, Python and Node can fail before project code runs:

- `python -c "import asyncio"` raises `WinError 10106`
- `node -e "console.log('node ok')"` fails at `ncrypto::CSPRNG`
- `cmd`, `Start-Process`, `rg`, `pyright`, or `pip-audit` behave inconsistently
- `codex exec` fails with DNS errors such as `os error 11003` in one shell, while the same command succeeds after explicitly setting `HTTP_PROXY` / `HTTPS_PROXY`

## Root Cause

There are two different failure layers:

1. The Windows network provider or Winsock catalog is actually broken. In that case, the same probes fail in a fresh elevated PowerShell.
2. The host is healthy, but the current agent process inherited an incomplete Windows process environment. The common missing variables are `ComSpec`, `SystemRoot`, `WINDIR`, `APPDATA`, `LOCALAPPDATA`, `PROGRAMDATA`, and `ProgramFiles`.
3. The host and local proxy are healthy, but proxy variables never entered the already-running parent process. `config.toml` and User/Machine environment changes are not hot-loaded by an existing PowerShell or Codex process.

Do not treat layer 2 as a repository logic bug or keep rerunning gates unchanged. Normalize the process environment first, then rerun the gate.

## Required Fix Pattern

PowerShell entrypoints that start Python, Node, Codex, or child PowerShell processes must run:

```powershell
. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment
```

Python subprocess helpers on Windows must normalize the child environment before `subprocess.run`, including:

- `SystemRoot`
- `WINDIR`
- `ComSpec`
- `SystemDrive`
- `HOMEDRIVE`
- `HOMEPATH`
- `APPDATA`
- `LOCALAPPDATA`
- `PROGRAMDATA`
- `ProgramFiles`

When a local proxy is part of the working Codex profile, the initializer must import only safe, non-secret variables from Codex `shell_environment_policy.set` or User/Machine environment:

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`
- `NO_PROXY`
- lowercase proxy aliases when present

Do not import tokens or API keys as part of this recovery path.

The initializer also prepends existing Windows system paths and default Git/GitHub CLI install paths to the process `PATH` so wrappers do not misdiagnose `git` or `gh` as missing when the agent process started with a stripped environment.

Target repo one-click governance baselines must carry a profile-level rule named `windows_process_environment_policy` so target repos do not regress when the baseline is re-applied.

## Diagnosis

Run these probes in the failing process and in a fresh elevated PowerShell:

```powershell
'ComSpec=' + $env:ComSpec
'SystemRoot=' + $env:SystemRoot
'WINDIR=' + $env:WINDIR
'APPDATA=' + $env:APPDATA
'LOCALAPPDATA=' + $env:LOCALAPPDATA
'PROGRAMDATA=' + $env:PROGRAMDATA
'ProgramFiles=' + $env:ProgramFiles
'HTTP_PROXY=' + $env:HTTP_PROXY
'HTTPS_PROXY=' + $env:HTTPS_PROXY
'NO_PROXY=' + $env:NO_PROXY
python -c "import asyncio; print('asyncio ok')"
node -e "console.log('node ok')"
```

For Codex network failures, a `405 Method Not Allowed` from `https://chatgpt.com/backend-api/wham/apps` through `127.0.0.1:10808` is a proxy reachability signal, not a Codex API success signal. If that probe works and `codex exec` works only when proxy env vars are explicitly set, normalize or restart the parent process before changing repository code.

On Windows, avoid hard-coding the exact `.exe` executable name. Use `codex`, `codex.cmd`, or a configurable `--codex-bin` / `GOVERNED_RUNTIME_CODEX_BIN` value unless that executable file has been verified on that machine.

If the fresh elevated PowerShell passes but the agent process fails, restart or normalize the agent process environment. If both fail, repair Windows networking:

```powershell
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
shutdown /r /t 0
```

## Verification

After changes, run:

```powershell
python -m pytest tests/runtime/test_subprocess_guard.py tests/runtime/test_runtime_doctor.py -q
.\scripts\verify-repo.ps1
```

`doctor-runtime.ps1` should report:

- `OK windows-process-environment`
- `OK windows-process-environment-normalized:<vars>` when the current process started with missing variables
- `OK python-asyncio`
- `OK windows-node-csprng` when Node is installed and healthy

If `python-asyncio` still fails after environment normalization, treat it as a host-level Windows networking/provider problem and validate in a fresh elevated PowerShell before changing project code.
