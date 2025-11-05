Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\izak.oliveira\Desktop\SGP"

' Inicia o gerenciador que cuida do servidor e monitora o navegador
WshShell.Run "cmd /c call venv\Scripts\activate && python gerenciador_sistema.py", 0, False

Set WshShell = Nothing
