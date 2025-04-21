@echo off
echo Coda Lite Git Synchronization Script
echo ===================================
echo.

REM Set environment variables to bypass global config
set GIT_CONFIG_NOSYSTEM=1
set HOME=%CD%

echo Setting up local Git configuration...
git config --local user.name "Aladin147"
git config --local user.email "134957975+Aladin147@users.noreply.github.com"

echo.
echo Checking repository status...
git status

echo.
echo Would you like to commit all changes? (Y/N)
set /p commit_choice=

if /i "%commit_choice%"=="Y" (
    echo.
    echo Enter commit message (default: "Update Coda Lite with voice loop implementation"):
    set commit_msg=Update Coda Lite with voice loop implementation
    set /p custom_msg=
    
    if not "%custom_msg%"=="" (
        set commit_msg=%custom_msg%
    )
    
    echo.
    echo Adding all changes...
    git add .
    
    echo.
    echo Committing with message: "%commit_msg%"
    git commit -m "%commit_msg%"
)

echo.
echo Would you like to push to remote? (Y/N)
set /p push_choice=

if /i "%push_choice%"=="Y" (
    echo.
    echo Pushing to remote repository...
    git push origin master
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Push failed. Would you like to try with credentials? (Y/N)
        set /p cred_choice=
        
        if /i "%cred_choice%"=="Y" (
            echo.
            echo Enter your GitHub username:
            set /p username=
            
            echo.
            echo Enter your GitHub personal access token (will not be displayed):
            set /p "password="
            
            echo.
            echo Pushing with credentials...
            git push https://%username%:%password%@github.com/Aladin147/Coda_Lite.git master
        )
    )
)

echo.
echo Git synchronization completed!
pause
