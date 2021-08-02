Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strCurDir = WshShell.CurrentDirectory

gui_file = "sources\dfs_gui\dfs_gui.cmd"

gui_string = fso.BuildPath(strCurDir, "\python\python.exe ") & strCurDir & "\sources\dfs_gui\dfs_gui_main.py"
Set objFile = fso.CreateTextFile(gui_file, True)
objFile.Write gui_string & vbCrLf
objFile.Close 

DesktopPath = WshShell.SpecialFolders("Desktop")
Set link = WshShell.CreateShortcut(DesktopPath & "\INS-GPS Data Fusion System.lnk")
link.IconLocation = strCurDir & "\sources\dfs_gui\dfs_gui.ico"
link.TargetPath = strCurDir & "\sources\dfs_gui\dfs_gui.vbs"
link.WorkingDirectory = strCurDir & "\sources\dfs_gui"
link.Save

Set WshShell = Nothing