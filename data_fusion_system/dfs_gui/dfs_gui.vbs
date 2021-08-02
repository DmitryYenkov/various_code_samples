Set WshShell = CreateObject("WScript.Shell") 
strCurDir = WshShell.CurrentDirectory
WshShell.Run strCurDir & "\dfs_gui.cmd", 0
Set WshShell = Nothing