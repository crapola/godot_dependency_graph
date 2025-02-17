"""
Structures used to store project information.
"""

import argparse
import sys
from pathlib import Path
from typing import NamedTuple, Self

import analyzer


def print_error(*args,**kwargs)->None:
	""" Print to stderr. """
	print(*args,file=sys.stderr,**kwargs)

class Script(NamedTuple):
	""" GDScript file. """
	addon:str # Addon it belongs to, empty string for main project files.
	name:str # Name of class_name, otherwise the script's file base name.
	path:Path # Path relative to project root.
	dependencies:set[str] # Types referenced in the script.

	@classmethod
	def open(cls,script:Path,addon:str,relpath:Path)->Self:
		"""
		Get information from script. Both paths are absolute.
		"""
		text:str=analyzer.load_string(script)
		class_name:str|None
		deps:set[str]
		try:
			class_name,deps=analyzer.parse_script(text)
		except SyntaxError as se:
			print_error(f"Parse error when processing {script} at line {se.lineno}, column {se.offset}:")
			print_error(se.text)
			raise se
		class_name=class_name or script.name
		return cls(addon,class_name,relpath,deps)

class Project(NamedTuple):
	""" Project. """
	name:str
	path:Path
	scripts:list[Script]

	@classmethod
	def open(cls,args:argparse.Namespace)->Self:
		""" Open and build project according to arguments. """
		path:Path=args.project
		gd_paths:list[Path]=analyzer.project_script_paths(path)
		scripts:list[Script]=[]
		for x in gd_paths:
			try:
				relpath:Path=x.relative_to(path)
				addon:str=cls._addon_from_path(x.relative_to(path))
				s:Script=Script.open(x,addon,relpath)
				if args.class_only and s.name.endswith(".gd"):
					continue
				scripts.append(s)
			# pylint: disable=broad-except
			except Exception as e:
				print_error("Skipping",x)
				print_error("Reason:",e)
				#raise e
				continue
		return cls(path.stem,path,scripts)

	@classmethod
	def _addon_from_path(cls,relative_file_path:Path)->str:
		""" Return the addon a file belongs to, or empty string. """
		addon_name:str=""
		if relative_file_path.parts[0]=="addons":
			addon_name=relative_file_path.parts[1]
		return addon_name
