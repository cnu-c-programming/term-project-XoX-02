@echo off
rem grader.bat  -  Mini Student Shell 채점 스크립트 (Windows)
rem
rem 사용법:
rem   grader.bat [admin_path] [client_path] [students_csv]
rem   기본값: .\admin_shell.exe  .\client_shell.exe  .\students.csv
rem
rem Python 3.9+ 필요
python "%~dp0grader.py" %*
exit /b %ERRORLEVEL%
