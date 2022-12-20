! global.zpl
!
! Written by Kenneth E. Moore 9/4/92
!
PRINT "This program computes the global vertex"
PRINT "coordinates or orientations surface by" 
PRINT "surface."
PRINT
s=0
LABEL 1
s = s+1
PRINT "Surface  = ", s
PRINT "Global X = ", GLCX(s)
PRINT "Global Y = ", GLCY(s)
PRINT "Global Z = ", GLCZ(s)
PRINT "Global L = ", GLCA(s)
PRINT "Global M = ", GLCB(s)
PRINT "Global N = ", GLCC(s)
IF s < NSUR() THEN GOTO 1
PRINT "All done!"


