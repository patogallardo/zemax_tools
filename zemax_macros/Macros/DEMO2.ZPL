! demo2.zpl
!
! This demonstration macro also calculates the transverse
! component of lateral color between the minimum and maximum
! wavelengths, similar to the demo1.zpl sample macro.  However,
! this macro demonstrates additional capabilities of the ZEMAX
! Programming Language which make the macro more robust.

INPUT "Enter pupil increment:", step
IF ((step <= 0) | (step >= 1.0))
	PRINT "Error: invalid step size"
	PRINT "Should be fraction, such as .1"
	GOTO 1
ENDIF

nw = NWAV()
IF (nw == 1)
	PRINT "There is only one wavelength defined!"
	GOTO 1
ELSE
	minwav = 1
	maxwav = 1
	FOR i = 2, nw, 1
		IF (WAVL(minwav) > WAVL(i)) THEN minwav = i
		IF (WAVL(maxwav) < WAVL(i)) THEN maxwav = i
	NEXT
ENDIF
! minwavnum and maxwavnum contain the min and max wavelength values

PRINT "Minimum wavelength = ", WAVL(minwav), " microns"
PRINT "Maximum wavelength = ", WAVL(maxwav), " microns"

IF (UNIT() == 0) THEN PRINT "Units are mm"
IF (UNIT() == 1) THEN PRINT "Units are cm"
IF (UNIT() == 2) THEN PRINT "Units are in"
IF (UNIT() == 3) THEN PRINT "Units are meters"

numsteps = 1/step

FOR i = 0, numsteps, 1
	py = i * step
	IF (py > 1.0) THEN py = 1.0

	RAYTRACE 0, 0, 0, py, minwav
	IF (RAYE())
		PRINT "Ray error occured.."
		GOTO 1
	ENDIF
	yf = RAYY(NSUR())

	RAYTRACE 0, 0, 0, py, maxwav
	IF (RAYE())
		Print "Ray error occured.."
		GOTO 1
	ENDIF
	yc = RAYY(NSUR())

	Print "Pupil zone = ", py, " ZTCA = ", yf - yc
NEXT

LABEL 1
