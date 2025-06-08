good now let's reason a bit aobut the models 
up till now we have been analyziing tiles/blocks which are two diamonds above the other 
next is going to be walls -- walls cover a quarter diamond 
this is an example cropped this is 205x263 -- this interesgly will fit perfectwil with the 401 width blocks (I know crazy) 
and this is due to the 4 pixels depth showing on teh second screenshot 
each frane is ad irection (N  E S  W )  showing you N and E directions 

actually to be more accuracte 
frame 0 --> connectnts West and North corners 
frame 1 --> North to East
frame 2 --> East to South
Frame 3--> south to west

we are still interesting in obtaining 8 points - the object is still two romboids but is not a diamond anymore 

we can still do things thankfully - a lot of things knowing the actual width 
let's take example the first image which is  N perspective (or W-> N segment) ~ works the same for south which is S --> E segment

we currently have deducible 3 points from  the bottom romboid

west, sout, and west  for bottom romboid 

west is the first point of contaxt from bottom left corner going up 
south is first point of contaxt from bottom left going right 
east is the first point of contact from bottom right going up 



