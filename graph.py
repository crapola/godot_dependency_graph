"""
Graph class stores relationships.
"""

class Graph:
	""" Graph structure. """
	def __init__(self)->None:
		self.nodes:dict[str,set[str]]={}

	def add(self,a:str,b:str)->None:
		""" Add relation a -> b """
		# Ignore self-references.
		if a==b:
			return
		if not self.nodes.get(a):
			self.nodes[a]=set()
		self.nodes[a].add(b)

	def remove(self,node_name:str)->None:
		""" Remove <node_name> from the graph. """
		self.nodes.pop(node_name)
		for s in self.nodes.values():
			s.discard(node_name)

	def contains(self,node_name:str)->bool:
		""" Check if graph has <node_name>. """
		is_key:bool=node_name in self.nodes
		is_value:bool=[node_name in x for x in self.nodes.values()].count(True)>=1
		return is_key or is_value

	def count_downstream(self,node_name:str)->int:
		""" Count nodes downstream of <node_name>. """
		deps:set[str]=self.nodes.get(node_name,set())
		i:int=len(deps)
		for subnode in deps:
			i+=self.count_downstream(subnode)
		return i

	def count_upstream(self,node_name:str,recurse:bool=True)->int:
		""" Count nodes upstream of <node_name>. """
		i=0
		for k,v in self.nodes.items():
			for n in v:
				if n==node_name:
					i+=1
					if recurse:
						i+=self.count_upstream(k)
		return i

	def is_bidirectional(self,a:str,b:str)->bool:
		""" Check a <-> b. """
		return b in self.nodes.get(a,{}) and a in self.nodes.get(b,{})

	# def rank(self)->str:
	# 	""" Rank nodes and return string containing DOT rank instructions. """
	# 	rank_dict:dict=swapped_dict({k:len(v) for k,v in self.nodes.items()})
	# 	sorted_ranks:list=sorted(rank_dict.items(),reverse=True)
	# 	print(sorted_ranks)
	# 	return "\n".join(["{rank=same;"+";".join(x[1])+";}" for x in sorted_ranks])

def swapped_dict(d:dict)->dict:
	""" Return new dict where keys and values are swapped. """
	x:dict={}
	for k,v in d.items():
		x.setdefault(v,[]).append(k)
	return x
