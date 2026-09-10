' Content Curator — start the app with NO console window, then open the browser.
' Run setup.bat (or run_app.bat) once first to install everything.
' The server stops itself a while after you close the browser tab, or use the
' Quit button in the app's sidebar.
Option Explicit

Dim sh, fso, root, url, health
Set sh  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = root
url    = "http://localhost:8501"
health = "http://127.0.0.1:8501/_stcore/health"

If Not fso.FileExists(root & "\.venv\Scripts\streamlit.exe") Then
    MsgBox "Please double-click setup.bat (or run_app.bat) once first to install everything.", _
           vbExclamation, "Content Curator"
    WScript.Quit 1
End If

Function IsUp()
    IsUp = False
    On Error Resume Next
    Dim h : Set h = CreateObject("MSXML2.XMLHTTP")
    h.Open "GET", health, False
    h.Send
    If Err.Number = 0 And h.Status = 200 Then IsUp = True
    On Error GoTo 0
End Function

If Not IsUp() Then
    sh.Run "cmd /c ollama serve", 0, False
    sh.Run """.venv\Scripts\streamlit.exe"" run src\app.py --server.headless=true --server.port=8501", 0, False
    Dim i
    For i = 1 To 60
        If IsUp() Then Exit For
        WScript.Sleep 1000
    Next
End If

sh.Run url, 1, False
