@echo off
echo Pushing changes to remote repository...

REM Set Git configuration locally (in case it wasn't set by the commit script)
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

REM Push to remote
git push origin master

echo Done!
