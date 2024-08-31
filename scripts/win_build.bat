@echo off
python -m venv --clear --upgrade-deps .venv_build
call .venv_build\Scripts\activate
pip install .
pip install .[build]
if exist "dist\" rm -r dist\
pyinstaller --clean --console --hide-console hide-late --noupx --icon=.\media\yacc.ico --add-binary media\y.ico:media --onefile .\yacc\yacc.py -p .\yacc
if %errorlevel% equ 0 (
    rm -r build\
)
call deactivate
