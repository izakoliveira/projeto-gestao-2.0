Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "executar_sistema.bat" & Chr(34), 0
Set WshShell = Nothing
