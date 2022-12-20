! centroid.zpl
!
! Written by Kenneth Moore 9/1/92
! Added TIMER function 4/18/96
!
TIMER
!
! The delta controls how many rays will be traced. A
! delta of .025 will trace a 80 x 80 grid in the pupil.
!
delta = .025
!
PRINT "This program computes the chief ray coordinates,"
PRINT "centroid coordinates, and middle coordinates for" 
PRINT "the primary wave spot at each field position."
maxfield = MAXF()
IF (maxfield == 0) THEN maxfield = 1
n = NSUR()
f = 1
LABEL 1
hx = FLDX(f)/maxfield
hy = FLDY(f)/maxfield
RAYTRACE hx, hy, 0, 0
FORMAT 10.4
PRINT
PRINT "  X Field    = ", FLDX(f),
PRINT "  Y Field    = ", FLDY(f)
PRINT "  X Chief    = ", RAYX(n),
PRINT "  Y Chief    = ", RAYY(n)
xraymax = -9e9
yraymax = -9e9
xraymin =  9e9
yraymin =  9e9
xraytot = 0
yraytot = 0
numray = 0
numrayattempt = 0
px = -1 - delta
LABEL 2
px = px + delta
py = -1 - delta
LABEL 3
py = py + delta
rad = px*px + py*py
IF (rad <= 0.9999999)
        RAYTRACE hx, hy, px, py
        numrayattempt = numrayattempt+1
        IF !rayv(n)
                numray = numray + 1
                x = RAYX(n)
                y = RAYY(n)
                IF (x < xraymin) THEN xraymin = x
                IF (x > xraymax) THEN xraymax = x
                IF (y < yraymin) THEN yraymin = y
                IF (y > yraymax) THEN yraymax = y
                xraytot = xraytot + x
                yraytot = yraytot + y
        ENDIF
ENDIF
IF (py < 1.0) THEN GOTO 3
IF (px < 1.0) THEN GOTO 2
IF (numray)
        FORMAT 14.8
        PRINT "  X Centroid = ", xraytot/numray,
        PRINT "  Y Centroid = ", yraytot/numray
        PRINT "  X Middle   = ", (xraymax+xraymin)/2,
        PRINT "  Y Middle   = ", (yraymax+yraymin)/2
        FORMAT .0
        PRINT "  ", numray, " out of ", numrayattempt," rays made it through."
ELSE
        PRINT "  No rays made it through!"
ENDIF
f=f+1
IF (f<= NFLD()) THEN GOTO 1
PRINT
PRINT "All field positions done!"
FORMAT 0.1
PRINT "Elapsed time ", ETIM(), " seconds."
