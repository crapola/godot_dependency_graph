"""
Classes and functions for the graph generator.
"""
import functools
import pathlib
import typing

import gdtoolkit.parser
import lark


def load_string(path:pathlib.Path)->str:
	""" Load a string from file at <path>. """
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
		tree:lark.Tree=gdtoolkit.parser.parser.parse(text)
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
	tokens:typing.Iterator=tree.scan_values(predicate_type_hints)
	collected_tokens=set(x.value for x in list(tokens))
	if extends:
		collected_tokens.add(extends)
	# Split combined types such as A.B, Array[float], Dictionary[A,B].
	# Use a tuple so we can modify the actual set during iteration.
	x:str
	for x in tuple(collected_tokens):
		if "[" in x or "." in x:
			types:list[str]=x.replace(",","[").replace(".","[").replace("]","[").split("[")[:-1]
			#print(x," split into ",types)
			collected_tokens.discard(x)
			collected_tokens.update(set(types))
	# Remove built-in types.
	godot_types:set[str]=godot_built_in_types()
	collected_tokens.difference_update(godot_types)
	return (class_name,collected_tokens)

def project_script_paths(path:pathlib.Path)->list[pathlib.Path]:
	"""
	List absolute paths to GDScript files (.gd) in the project
	located at <path>, including the content of addons/.
	"""
	scripts:typing.Generator[pathlib.Path,None,None]=path.rglob("*.gd")
	return list(scripts)

@functools.cache
def godot_built_in_types()->set[str]:
	"""
	Get set of all built-in types and native classes.

	class_list.txt was generated in Godot using:
		FileAccess.open("res://class_list.txt",FileAccess.WRITE).store_csv_line(ClassDB.get_class_list())

	built_ins.txt was hand written...
	"""
	def local_path(filename:str)->pathlib.Path:
		return pathlib.Path(__file__).parent.joinpath(pathlib.Path(filename))
	with open(local_path("class_list.txt"),"rt",encoding="utf-8") as f1,\
		 open(local_path("built_ins.txt"),"rt",encoding="utf-8") as f2:
		classes=set(f1.read().split(","))
		built_ins=set(f2.read().split("\n"))
		#print("Loaded:",f1,f2)
		return classes.union(built_ins)
