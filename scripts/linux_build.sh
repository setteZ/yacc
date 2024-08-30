#! /bin/bash
python -m venv --clear --upgrade-deps .venv_build
source .venv_build/bin/activate
pip install .
pip install .[build]
if [ -d "build" ]; then
  rm -r build
fi
if [ -d "dist" ]; then
  rm -r dist
fi
pyinstaller --icon=./media/yacc.ico --onefile ./yacc/yacc.py -p ./yacc
if [ $? -eq 0 ]; then
  rm -r build
fi
deactivate