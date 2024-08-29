#! /bin/bash
if [ ! -d "build_venv" ]; then
  python -m venv build_venv
fi
source build_venv/bin/activate
python -m pip install --upgrade pip
pip install .
pip install .[build]
if [ -d "build" ]; then
  rm -r build
fi
if [ -d "dist" ]; then
  rm -r dist
fi
pyinstaller --icon=./media/yacc.ico --onefile ./yacc/yacc.py -p ./yacc
if [ -d "build" ]; then
  rm -r build
fi
deactivate
rm -r build_venv