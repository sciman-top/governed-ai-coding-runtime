# Windows Process Environment Recovery

## Symptom

In Codex, CI wrappers, or reduced PowerShell sessions, Python and Node can fail before project code runs:

- `python -c "import asyncio"` raises `WinError 10106`
- `node -e "console.log('node ok')"` fails at `ncrypto::CSPRNG`
- `cmd`, `Start-Process`, `rg`, `pyright`, or `pip-audit` behave inconsistently

## Root Cause

There are two different failure layers:

1. The Windows network provider or Winsock catalog is actually broken. In that case, the same probes fail in a fresh elevated PowerShell.
2. The host is healthy, but the current agent process inherited an incomplete Windows process environment. The common missing variables are `ComSpec`, `SystemRoot`, `WINDIR`, `APPDATA`, `LOCALAPPDATA`, and `PROGRAMDATA`.

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
python -c "import asyncio; print('asyncio ok')"
node -e "console.log('node ok')"
```

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
