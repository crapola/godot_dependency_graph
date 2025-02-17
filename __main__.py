"""
--------------------------------
Godot dependency graph generator
--------------------------------
"""

import argparse
import sys
from pathlib import Path

import formatting
from project import Project


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
	parser.add_argument("--folders",
		action=argparse.BooleanOptionalAction,
		default=True,
		help='display folders.')
	return parser.parse_args(args)

def main()->None:
	""" main() """
	args:argparse.Namespace=parse_arguments()
	output:str=formatting.dot_from_project(Project.open(args),args.folders)
	if args.output:
		with open(args.output,"wt",encoding="utf-8") as f:
			f.write(output)
		print("Output saved to",args.output)
	else:
		print(output)

if __name__=="__main__":
	main()
