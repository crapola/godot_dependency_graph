"""
Text formatting.
"""

def wrap_indented_block(text_lines:str)->str:
	""" Wrap indented block lines between braces. """
	wrapped:str="{\n\t"+"\t".join(text_lines.splitlines(True))+"}\n"
	return wrapped
