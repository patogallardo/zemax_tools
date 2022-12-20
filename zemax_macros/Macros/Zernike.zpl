! This macro computes the first 37 Zernike Fringe coefficients
! for the currently loaded lens, at wavelength 1, field 1, and with a 
! 32 x 32 grid density (sampling =1).  The coefficients are placed
! in vector 1.

! First get the data:
maxt = 37
GETZERNIKE maxt,1,1,1,1
FORMAT 16.6
! Then print out the data
PRINT "Peak to Valley : ", VEC1(1)
PRINT "RMS to zero    : ", VEC1(2)
PRINT "RMS to mean    : ", VEC1(3)
PRINT "RMS to centroid: ", VEC1(4)
PRINT "Variance       : ", VEC1(5)
PRINT "Strehl ratio   : ", VEC1(6)
PRINT "RMS Fit Error  : ", VEC1(7)
PRINT "Maximum Fit Error : ", VEC1(8)
i = 1
LABEL 1
	FORMAT 2.0
	PRINT "Zernike #", i, " = ",
	FORMAT 16.6
	PRINT vec1(8+i)
	i = i + 1
IF (i <= maxt) THEN GOTO 1
PRINT "All Done!"

