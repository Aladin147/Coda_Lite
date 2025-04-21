@echo off
echo Committing changes to Coda Lite repository...

REM Set Git configuration locally
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Add all changes
git add .

REM Commit the changes
git commit -m "Complete voice loop implementation with GPU acceleration"

REM Push to remote (uncomment when ready)
REM git push origin master

echo Done!
