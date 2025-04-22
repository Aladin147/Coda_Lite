@echo off
echo Committing fix for JSON leakage in tool responses to Coda Lite repository...

REM Set Git configuration locally
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Add all changes
git add .

REM Commit the changes
git commit -m "Fix JSON leakage in tool responses with robust scrubbing and real-time tool execution (v0.0.6)"

REM Push to remote (uncomment when ready)
REM git push origin master

echo Done!
