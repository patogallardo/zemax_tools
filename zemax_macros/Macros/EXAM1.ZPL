! exam1.zpl
!
! Written by Kenneth E. Moore 8/19/94
!
! This macro is the Example 1 macro from the very end of 
! Chapter 22 (ZPL Chapter) of the ZEMAX User's Guide.
!
! This macro prints out the chief ray coordinates on the image surface
! for each field position.
!
nfield = NFLD()
maxfield = MAXF()
! prevent divide by zero bug
IF (maxfield == 0.0) THEN maxfield = 1.0;
n = NSUR()
FOR i, 1, nfield, 1
        hx = FLDX(i)/maxfield
        hy = FLDY(i)/maxfield
        PRINT "Field number ", i
        RAYTRACE hx,hy,0,0,PWAV()
        PRINT "X-field angle : ", FLDX(i)," Y-field angle : ", FLDY(i)
        PRINT "X-chief ray   : ", RAYX(n), " Y-chief ray   : ", RAYY(n)
        PRINT
NEXT
PRINT "All Done!"
