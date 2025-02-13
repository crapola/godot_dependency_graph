"""
--------------------------------
Godot dependency graph generator
--------------------------------
"""

import argparse
import sys
from pathlib import Path
from typing import NamedTuple, Self

import analyzer
import formatting
import graph


def print_error(*args,**kwargs)->None:
	""" Print to stderr. """
	print(*args,file=sys.stderr,**kwargs)

def parse_arguments()->argparse.Namespace:
	""" Handle command line arguments. """
	args:list[str]=sys.argv[1:]
	parser=argparse.ArgumentParser(
		"godot_dependency_graph",
		"python godot_dependency_graph <project> [options]",
		"description: build a Graphviz .dot file showing dependencies in a Godot project.")
	parser.add_argument("project",
		action='store',
		type=Path,
		help='path to Godot project')
	parser.add_argument("--output",
		action='store',
		type=Path,
		help='path to output. If not provided, write to stdout.')
	parser.add_argument("--class-only",
		action=argparse.BooleanOptionalAction,
		default=False,
		help='only process scripts that define a class_name')
	return parser.parse_args(args)

class Script(NamedTuple):
	""" Information about a GDScript file. """
	addon:str # Addon it belongs to, empty string for main project files.
	name:str # Name of class_name, otherwise the script's file base name.
	dependencies:set[str] # Types referenced in the script.

	@classmethod
	def open(cls,project:Path,script:Path)->Self:
		"""
		Get information from script, or None in case of parse errors.
		Both paths are absolute.
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
			#return None
		class_name=class_name or script.name
		addon_name:str=Script._addon_from_path(script.relative_to(project))
		return cls(addon_name,class_name,deps)

	@staticmethod
	def _addon_from_path(relative_file_path:Path)->str:
		""" Return the addons/ folder name a file belongs to, or empty string. """
		addon_name:str=""
		if relative_file_path.parts[0]=="addons":
			addon_name=relative_file_path.parts[1]
		return addon_name

class Project(NamedTuple):
	""" Project information. """
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
				s:Script=Script.open(path,x)
				if args.class_only and s.name.endswith(".gd"):
					continue
				scripts.append(s)
			except Exception as e:
				print_error("Skipping",x)
				print_error("Reason:",e)
				continue
		return cls(path.stem,path,scripts)

def dot_from_project(project:Project)->str:
	""" Create the .dot text. """
	# Build graph.
	g=graph.Graph()
	for script in project.scripts:
		for d in script.dependencies:
			g.add(script.name,d)
	rels:str=str(g)

	# TODO: bidirectional arrows
	# A->B and B->A should become
	# A->B [dir=both]
	# and color those red
	#rels='\n'.join([x[:-1]+' [color="blue:red;0.001"]' for x in rels.splitlines()])

	digraph_stuff:str=";\n".join((
		"rankdir=LR", # Left to right.
		'',
	))

	body:str=digraph_stuff+rels

	# Give classless scripts a grey background.
	for k in g.nodes:
		if k.endswith('.gd'):
			body+=f'"{k}" [style=filled];\n'

	# Display addons in clusters.
	def get_class_addon(p:Project,name:str)->str:
		""" Find addon where a class name is defined. """
		for s in p.scripts:
			if s.name==name:
				return s.addon
		return ""
	clusters:dict={}
	for s in project.scripts:
		classes:set[str]=set([s.name]).union(s.dependencies)
		for c in classes:
			addon:str=get_class_addon(project,c)
			if addon!="" and g.contains(c):
				clusters[addon]=clusters.get(addon,"")+'"'+c+'"'+"\n"
	cluster=""
	for k,v in clusters.items():
		cluster=v
		cluster+=f'label="{k}"'
		cluster:str=formatting.wrap_indented_block(cluster)
		cluster=f"subgraph cluster_{k} "+cluster
	body+=cluster

	output:str="digraph "+formatting.wrap_indented_block(body)
	return output

def main()->None:
	""" main() """

	args:argparse.Namespace=parse_arguments()
	p:Project=Project.open(args)
	output:str=dot_from_project(p)
	if args.output:
		with open(args.output,"wt",encoding="utf-8") as f:
			f.write(output)
		print("Output saved to",args.output)
	else:
		print(output)

if __name__=="__main__":
	main()
