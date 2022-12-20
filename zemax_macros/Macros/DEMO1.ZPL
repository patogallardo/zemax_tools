! demo1.zpl
!
! This demonstration macro traces the chief ray at incremental 
! pupil positions for two separate wavelengths.  The real ray
! y height at the image plane is calculated for each pupil ray,
! and the transverse component of lateral color is calculated by
! the difference in height between the two wavelengths.

numsteps = 10
FOR i = 0, numsteps, 1
	py = i / numsteps
	RAYTRACE 0, 0, 0, py, 1
	yf = RAYY(NSUR())
	RAYTRACE 0, 0, 0, py, 3
	yc = RAYY(NSUR())
	PRINT "Pupil zone = ", py, " ZTCA = ", yf - yc
NEXT