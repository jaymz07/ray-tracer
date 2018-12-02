Simple 2D ray tracing program. Useful for "playing around" with optical configurations. The initial rays are currently set inside of the code, but the optical elements (currently just mirrors) can be fully manipulated with user input. Output is computed and drawn in real time, giving the progam a "video game feel".

------Requirements---------

The following python libraries are used:

pygame, numpy

These can be installed with:

	pip install pygame

or, for python3:

	pip3 install pygame

if your path does not recognize pip3:
	
	python3 -m pip install pygame

if none of the above works, try

	pip install --upgrade pip
	
or
	(pip3 install --upgrade pip)
	(python3 -m pip install --upgrade pip)

and retry the above steps.


-----Usage------------

There is no installation. Simply run the rayTracer.py using

	python rayTracer.py



-----Mouse input------

Moving the mouse around, you can see that optical elements are "selected" when the mouse is nearby.

-Right Click/Drag
	pans the view

-left click/drag
	move optical element

-mouse wheel
	zoom view



------Keyboard Input-----

KEY: R
	Rotate the selected element. Click to stop rotating

KEY: S
	Change the size of selected element. Click to accept.

KEY: 0
	Reset to original view

KEY: N
	Add new mirror at location of mouse

KEY: Backspace
	Remove last added element
