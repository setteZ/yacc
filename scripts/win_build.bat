@echo off
python -m venv --clear --upgrade-deps .venv_build
call .venv_build\Scripts\activate
pip install .
pip install .[build]
if exist "dist\" rm -r dist\
pyinstaller --clean --console --hide-console hide-late --noupx --icon=.\media\yacc.ico --add-binary media\y.ico:media --onefile .\yacc\yacc.py -p .\yacc --hidden-import can.interfaces.kvaser --hidden-import can.interfaces.ixxat --hidden-import can.interfaces.pcan
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

set "versione=!versione:"=!"
set "version=%version:~1%"
for /f "delims=" %%s in ('python -c "import sys; print(sys.argv[1].lower())" %PROCESSOR_ARCHITECTURE%') do set PROC_ARCH=%%s
set "zip_name=yacc_%version%_windows_%PROC_ARCH%.zip"
echo %zip_name%
mkdir publish
cd dist
where 7z /q
if %errorlevel% neq 0 goto missing7z
7z a %zip_name% yacc.exe
goto publish_cmd
:missing7z
where zip /q
if %errorlevel% neq 0 goto missingcompression
zip %zip_name% yacc.exe
goto publish_cmd
:missingcompression
echo missing a compression program
goto exiterror

:publish_cmd
move %zip_name% ..\publish 
goto :eof

:exiterror
exit /b 1
