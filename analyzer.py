"""
Classes and functions for the graph generator.
"""
import os

import gdtoolkit.parser
import lark


class Graph:
	""" Graph structure. """
	def __init__(self)->None:
		self.nodes:dict[str,set[str]]={}

	def add(self,a:str,b:str)->None:
		""" Add relation a -> b """
		if b in godot_built_in_types(): # TODO: cache?
			# Ignore if b is a Godot type.
			return
		if not self.nodes.get(a):
			self.nodes[a]=set()
		self.nodes[a].add(b)

	def __str__(self)->str:
		""" DOT language output. """
		s:str=""
		for k,v in self.nodes.items():
			for b in v:
				s+=f"\t{k} -> {b};\n"
		# Grey background for scripts.
		for k in self.nodes:
			if k.endswith('.gd"'):
				s+=f"{k} [style=filled];\n"
		# Additional formatting.
		s+="beautify=true;pack=true;rankdir=LR;\n"
		return f"digraph {{\n{s}}}"

def godot_built_in_types()->set[str]:
	"""
	Get set of all built-in types and native classes.

	class_list.txt was generated in Godot using:
		FileAccess.open("res://class_list.txt",FileAccess.WRITE).store_csv_line(ClassDB.get_class_list())

	built_ins.txt was hand written...
	"""
	def local_path(filename:str)->str:
		return os.path.join(os.path.dirname(__file__),filename)
	with open(local_path("class_list.txt"),"rt",encoding="utf-8") as f1,\
		 open(local_path("built_ins.txt"),"rt",encoding="utf-8") as f2:
		classes=set(f1.read().split(","))
		built_ins=set(f2.read().split("\n"))
		return classes.union(built_ins)

def load_script(path:str)->str:
	""" Load script into string. """
	with open(path,"rt",encoding="utf-8") as f:
		return f.read()

def parse_script(text:str)->tuple[str|None,set[str]]:
	"""
	Parse using gdtoolkit.
	Return tuple containing:
		str: The script's class_name or None.
		set[str]: Types referenced in the script.
	Raise a SyntaxError if parsing fails.
	"""
	try:
		tree=gdtoolkit.parser.parser.parse(text)
	except lark.exceptions.UnexpectedInput as e:
		#raise e
		raise SyntaxError("Parse error",("", e.line, e.column, e.get_context(text))) from e
	# Script class name.
	class_name_branch=list(tree.find_data("classname_stmt"))
	if class_name_branch:
		class_name:str|None=class_name_branch[0].children[0].value
	else:
		class_name=None
	# Extends.
	extends_branch=list(tree.find_data("extends_stmt"))
	if extends_branch:
		extends:str|None=extends_branch[0].children[0].value
	else:
		extends=None
	# Type hints.
	def predicate_type_hints(x)->bool:
		return isinstance(x,lark.Token) and x.type=='TYPE_HINT'
	tokens=tree.scan_values(predicate_type_hints)
	collected_tokens=set(x.value for x in list(tokens))
	if extends:
		collected_tokens.add(extends)
	return (class_name,collected_tokens)

def project_scripts(path:str)->list[str]:
	""" Return list of GDScript files in the project located at <path>. """
	result:list[str]=[]
	for root,_dirs,files in os.walk(path):
		for file in files:
			if file.endswith(".gd"):
				result.append(os.path.join(root,file))
	return result
