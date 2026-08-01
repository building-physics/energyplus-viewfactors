@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Run from the repository root, regardless of the caller's current directory.
pushd "%~dp0.." || exit /b 1

set "PYFILES="
for /F "delims=" %%F in ('git ls-files "*.py"') do set "PYFILES=!PYFILES! "%%F""

if not defined PYFILES (
    echo No tracked Python files were found.
    goto :failed
)

echo Fixing lint violations...
ruff check --fix --force-exclude !PYFILES! || goto :failed

echo Formatting Python files...
ruff format --force-exclude !PYFILES! || goto :failed

set "TYPEFILES="
for /F "delims=" %%F in ('git ls-files "*.py" ^| findstr /B /C:"src/energyplus_viewfactors/" /C:"tests/"') do set "TYPEFILES=!TYPEFILES! "%%F""

if not defined TYPEFILES (
    echo No tracked package or test Python files were found.
    goto :failed
)

echo Checking types...
mypy !TYPEFILES! || goto :failed

echo Quality fixes and type checks completed.
popd
exit /b 0

:failed
echo Quality fixes failed.
popd
exit /b 1
