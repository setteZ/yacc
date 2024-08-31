@echo off
python -m venv --clear --upgrade-deps .venv_build
call .venv_build\Scripts\activate
pip install .
pip install .[build]
if exist "dist\" rm -r dist\
pyinstaller --clean --console --hide-console hide-late --noupx --icon=.\media\yacc.ico --add-binary media\y.ico:media --onefile .\yacc\yacc.py -p .\yacc
if %errorlevel% neq 0 (
    echo "there's been an error"
    goto :eof
)
rm -r build\
call deactivate

setlocal enabledelayedexpansion

set "file_input=..\\yacc\\yacc\\__init__.py"

for /f "tokens=*" %%i in ('findstr "__version__" "%file_input%"') do (
    set "linea=%%i"
)

for /f "tokens=2 delims==" %%j in ("!linea!") do (
    set "version=%%j"
)

set "version=%version:~1%"
set "zip_name=yacc_%version%_windows_%PROCESSOR_ARCHITECTURE%.zip"
echo %zip_name%
mkdir .\publish
cd dist
7z a %zip_name% yacc.exe
move %new_name% ..\publish 
