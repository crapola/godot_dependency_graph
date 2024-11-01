"""
--------------------------------
Godot dependency graph generator
--------------------------------
"""

import sys

import analyzer


def main()->None:
	""" main() """
	args:list[str]=sys.argv[1:]
	if not args:
		print("Usage: python godot_dependency_graph <path_to_project>")
		return
	gdscript_files:list[str]=analyzer.project_scripts(args[0])
	g=analyzer.Graph()
	for f in gdscript_files:
		text:str=analyzer.load_script(f)
		class_name:str|None
		deps:set[str]
		try:
			class_name,deps=analyzer.parse_script(text)
		except SyntaxError as se:
			print(f"Parse error when processing {f} at line {se.lineno}, column {se.offset}:")
			print(se.text)
			continue
		file_base_name:str=f.rsplit("\\")[-1]
		class_name=class_name or file_base_name
		for d in deps:
			# Handle typed containers.
			if "[" in d:
				types:list[str]=d.split("[")
				g.add(class_name,types[0])
				g.add(class_name,types[1][:-1])
			else:
				g.add(class_name,d)
	print(g)

if __name__=="__main__":
	main()
