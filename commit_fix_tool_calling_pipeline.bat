@echo off
echo Committing fix for tool calling pipeline to Coda Lite repository...

REM Set Git configuration locally
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Add all changes
git add .

REM Commit the changes
git commit -m "Fix tool calling pipeline with proper streaming and duplicate __init__ method (v0.0.9)"

REM Push to remote (uncomment when ready)
REM git push origin master

echo Done!
