!Edgesag.zpl

! This macro calculates the axial vertex to edge sag at 
! the semidiameter of each surface in the current lens file.
! This information may be used for grinding a lens.

FILE$  = $FILEPATH()
TITLE$ = $LENSNAME()

PRINT 
PRINT "File : ", FILE$
PRINT "Title: ", TITLE$
PRINT

PRINT
PRINT "VERTEX TO EDGE SAG DATA:"
PRINT

PRINT "SURF             SAG    SEMIDIAMETER"

n = NSUR()
GETSYSTEMDATA 1
st = VEC1(23)

FOR s = 1, n, 1
   x = 0
   y = SDIA(s)
   z = SAGG(x,y,s)

   IF (s == st)
      PRINT " STO",
   ELSE
      IF (s == n)
         PRINT " IMA",
      ELSE
         FORMAT 4.0
         PRINT s,
      ENDIF
   ENDIF

   FORMAT 14.4
   PRINT "  ",z,"  ",y
NEXT