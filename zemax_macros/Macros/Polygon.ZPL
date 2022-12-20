! Polygon generator

! Written by Mary G. Turner 4 Jan 2001


! This macro is used to generate a ZEMAX polygon object (*.POB) file to be used
! as a faceted radiometer. User specifies radius of containing circle, the number
! of edges to the "circle", length of the tube, and the number of sections
! along the length.
! File generates rectangular facets, ZEMAX translates to triangles.

pi = 2 * ACOS(0)
dtor = pi/180

ext$ = ".POB"
PATH$ = $OBJECTPATH()
D$ = "\Polygon Objects\"

INPUT "Radius of tube: ", rad
INPUT "Length of tube: ", len
INPUT "Number of edges around radius: ", n
INPUT "Number of sections in length: ", s
INPUT "Name of radiometer: ", name$

file$ = PATH$ + D$ + name$ + ext$

OUTPUT file$

! Calculate the Z coordinate for each section

start = 0
step = len/(s-1)

FOR j = 1, s, 1
   zval = start + (j-1)*step
   

   ! Calculate the X and Y coordinates of each vertex

   FOR i = 1, n, 1

      fang = 180/n
      inc = 360/n
   
      ang = fang + (i-1)*inc
      rang = dtor*ang
      xval = rad*COSI(rang)
      yval = rad*SINE(rang)
      
!     Print out the vertex coordinates
      PRINT "V ", INTE(n*(j-1) + i), " ", xval, " ", yval," ", zval
   
   NEXT i
NEXT j


FORMAT 4.0

! Print out the rectangles

FOR j = 1, s-1, 1
   FOR i = 1, n, 1
     IF i < n
        PRINT "R ", (j-1)*n +i," ", (j-1)*n +i+1 ," ", (j)*n +i+1," ", (j)*n + i
     ELSE
        PRINT "R ", (j-1)*n +i," ", (j-1)*n + 1 ," ", (j)*n +1," ", (j)*n + i
     ENDIF
   NEXT
NEXT   
