"""
Text formatting and dot generation.
"""

from typing import Iterable, Sequence

from graph import Graph
from project import Project
from pathlib import Path

Lines=Iterable[str]

def indent(lines:Lines)->Lines:
	return ["\t"+x for x in lines]

def join_lines(lines:Lines)->str:
	return "\n".join(lines)

def wrap(left:str,center:str,right:str)->str:
	return f'{left}{center}{right}'

def quotes(string:str)->str:
	return wrap('"',string,'"')

def indent_block(lines:Lines)->str:
	return join_lines(('{',*indent(lines),'}'))

def nodes(graph:Graph)->list[str]:
	""" Output node edges. """
	lines:list[str]=[]
	bidirs=set(frozenset({a,b}) for a,x in graph.nodes.items() for b in x if graph.is_bidirectional(a,b))
	for a,b in bidirs:
		lines.append(f'"{a}" -> "{b}" [dir=both;color=red;]')
	for k,v in graph.nodes.items():
		for x in v:
			if not frozenset({k,x}) in bidirs:
				lines.append(f'"{k}" -> "{x}"')
	return lines

def clusters(project:Project,graph:Graph)->list[str]:
	""" Create folders subgraphs. """
	lines:list[str]=[]
	dirs=dict()
	for script in project.scripts:
		parents:Sequence[Path]=script.path.parents
		dirs[parents]=dirs.get(parents,[])+[script.name]
	def subgraph(path:Path,nodes:list[str])->list[str]:
		"""
		Output lines that define a subgraph for the folder at <path>
		that contains <nodes>.
		"""
		if not path.parts:
			return []
		l:list[str]=[]
		# Nested subgraphs for this path.
		for p in path.parts:
			l.append(f'subgraph cluster_{p} {{label="{p}";')
		# Insert nodes.
		l+=[quotes(x) for x in nodes if graph.contains(x)]
		# Close braces.
		l.append(*['}'*len(path.parts)])
		return l
	for k,v in dirs.items():
		lines+=subgraph(list(k)[0],v)
	return lines

def dot_from_project(project:Project,folders=True)->str:
	""" Create the full .dot text for <project>. """
	g=Graph()
	for script in project.scripts:
		for d in script.dependencies:
			g.add(script.name,d)

	# Node edges.
	lines:list[str]=nodes(g)

	# Folders in clusters.
	if folders:
		lines+=clusters(project,g)

	# Give classless scripts a grey background.
	for k in g.nodes:
		if k.endswith('.gd'):
			lines.append(f'"{k}" [style=filled]')

	# Finalize digraph.
	lines.insert(0,"rankdir=LR")
	#lines.insert(0,"")
	output:str="digraph"+indent_block(lines)
	return output

