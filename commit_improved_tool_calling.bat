@echo off
echo Committing improved tool calling implementation to Coda Lite repository...

REM Set Git configuration locally
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Add all changes
git add .

REM Commit the changes
git commit -m "Improve tool calling with proper function call integration (v0.0.2)"

REM Push to remote (uncomment when ready)
REM git push origin master

echo Done!
