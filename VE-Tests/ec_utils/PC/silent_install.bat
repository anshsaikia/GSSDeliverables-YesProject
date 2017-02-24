if "%2" == "" (
    start /WAIT %1 /w /s /v/qn
    )
if "%~2" == "/x" (
    start /WAIT %1 %2 /w /s /v/qn
    )
echo Exit Code is %errorlevel%