Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\izak.oliveira\Desktop\SGP"

' Verificar se já está rodando
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMIService.ExecQuery("Select * from Win32_Process Where Name = 'python.exe'")

Dim alreadyRunning
alreadyRunning = False

For Each objProcess in colProcesses
    If InStr(objProcess.CommandLine, "app_producao.py") > 0 Then
        alreadyRunning = True
        Exit For
    End If
Next

' Se não está rodando, inicia
If Not alreadyRunning Then
    WshShell.Run "cmd /c call venv\Scripts\activate && python app_producao.py", 0, False
    WScript.Sleep 4000
Else
    WScript.Sleep 1000
End If

' Abre navegador na página de login
WshShell.Run "http://localhost:5000/login"
Set WshShell = Nothing
