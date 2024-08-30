@echo off
python -m venv --clear --upgrade-deps .venv_build
call .venv_build\Scripts\activate
pip install .
pip install .[build]
if exist "build\" rm -r build\
if exist "dist\" rm -r dist\
pyinstaller --icon=.\media\yacc.ico --onefile .\yacc\yacc.py -p .\yacc
if %errorlevel% equ 0 (
    rm -r build\
)
call deactivate