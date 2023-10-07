pyinstaller --onefile --noconsole --icon=.\src\booklet.ico .\src\constants.py .\src\gradesModule.py .\src\jsonHandler.py .\src\Libretto.py -n Libretto
move .\dist\Libretto.exe .
del Libretto.spec
rd /q/s .\dist .\build
CLS
@echo "Installation successful"
@pause