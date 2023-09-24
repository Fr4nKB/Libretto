pyinstaller --onefile --noconsole --icon=.\src\booklet.ico .\src\Libretto.py
move .\dist\Libretto.exe .
del Libretto.spec
rd /q/s .\dist .\build
CLS
@echo "Installation successful"
@pause