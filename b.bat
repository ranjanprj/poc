pyinstaller --key=Abcd23445243234344ladfa  --hidden-import=pandas --additional-hooks-dir=. -F --add-data "templates;templates" --add-data "static;static" --hidden-import=_cffi_backend  --icon=C:\3Projects\kaboodle\static\images\icon.ico app.py 


