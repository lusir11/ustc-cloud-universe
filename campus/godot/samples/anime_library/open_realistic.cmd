@echo off
if not defined GODOT_EXE set "GODOT_EXE=godot"
start "" "%GODOT_EXE%" --path "%~dp0..\.." res://samples/anime_library/realistic.tscn
