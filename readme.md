### GDScript dependency graph builder

This Python program attempts to build a dependency graph of the custom classes in a Godot project.  
It outputs the result as DOT language.
You can use it to generate the graph using whichever way your prefer, the easiest being pasting into an online service such as https://dreampuf.github.io/GraphvizOnline .

#### Installation and usage

[godot-gdscript-toolkit](https://github.com/Scony/godot-gdscript-toolkit) is required.

Run the program using:

	python godot_dependency_graph <path_to_project>

To show help and options, use:

	python godot_dependency_graph -h
