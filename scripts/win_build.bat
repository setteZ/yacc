@echo off
if not exist "build_venv\" python -m venv build_venv
call build_venv\Scripts\activate
python -m pip install --upgrade pip
pip install .
pip install .[build]
if exist "build\" rm -r build\
if exist "dist\" rm -r dist\
pyinstaller --icon=.\images\yacc.ico --onefile .\yacc\yacc.py -p .\yacc
if errorlevel 0 (
    rm -r build\
)
call deactivate && (rm -r build_venv\)