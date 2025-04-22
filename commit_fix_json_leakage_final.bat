@echo off
echo Committing final fix for JSON leakage to Coda Lite repository...

REM Set Git configuration locally
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Add all changes
git add .

REM Commit the changes
git commit -m "Fix JSON leakage with ultra-aggressive cleaning and direct fallbacks for time/date tools (v0.1.0)"

REM Push to remote (uncomment when ready)
REM git push origin master

echo Done!
