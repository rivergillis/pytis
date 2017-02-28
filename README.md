# Pytis
*A TIS-100 emulator written in Python*

Pytis is meant to be a program that fully supports the instruction set defined in the game TIS-100, as well as the support for IO between nodes. The Nodes are currently stored in a textfile that defines the node (x,y) location as well as the code contained within them, seperated by newlines.  

Nodes begin with open square brackets to signify a new x,y location. Example:
[0,0]
ADD 20
SUB 50
JRO -2

Will cause a Node to be created at (0,0) with the three lines of codes loaded.

The end-goal for this project is to have some sort of graphical user interface to allow the user to add nodes and to write code, as well as to execute and view the execution of the code as it is being executed.
  

