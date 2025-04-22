@echo off
echo Fixing GitHub connection and committing changes safely...

REM Deactivate virtual environment if active
if defined VIRTUAL_ENV (
    echo Deactivating virtual environment...
    call deactivate
)

REM Check Git status
echo Checking Git status...
git status

REM Configure Git if needed
echo Setting up Git configuration...
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Check remote connection
echo Checking remote connection...
git remote -v

REM Verify remote connection
echo Verifying connection to GitHub...
git ls-remote --exit-code origin
if %ERRORLEVEL% NEQ 0 (
    echo Error: Cannot connect to GitHub remote.
    echo Attempting to fix remote connection...

    REM Try to fix the remote connection
    git remote remove origin
    git remote add origin https://github.com/Aladin147/Coda_Lite.git

    REM Verify again
    git ls-remote --exit-code origin
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Still cannot connect to GitHub remote.
        echo Please check your network connection and GitHub credentials.
        exit /b 1
    ) else (
        echo Successfully reconnected to GitHub remote.
    )
) else (
    echo GitHub remote connection verified successfully.
)

REM Update README.md
echo Updating README.md...
move /Y README.md.new README.md

REM Stage changes
echo Staging changes...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Fix tool calling pipeline and document JSON leakage issue (v0.1.0)"

REM Ask before pushing
set /p PUSH_CONFIRM="Do you want to push changes to GitHub? (y/n): "
if /i "%PUSH_CONFIRM%"=="y" (
    echo Pushing changes to GitHub...
    git push origin master
    echo Push completed.
) else (
    echo Changes committed locally but not pushed to GitHub.
    echo To push later, run: git push origin master
)

echo Done!
