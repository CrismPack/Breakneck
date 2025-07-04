@echo off

cd Modpack-CLI-Tool
python -m venv env
call "venv\scripts\activate"
pip install -r requirements.txt
python Modpack-Export.py

pause