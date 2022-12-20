! exam2.zpl
!
! Written by Kenneth E. Moore 8/19/94
!
! This macro is the Example 2 macro from the very end of 
! Chapter 22 (ZPL Chapter) of the ZEMAX User's Guide.
!
! This macro computes an estimate of the RMS spot size using random rays.
!
PRINT "Primary wavelength is number ",
FORMAT .0
PRINT PWAV(),
FORMAT .4
PRINT " which is ", WAVL(PWAV()), " microns."
PRINT "Estimating RMS spot size for each wavelength."

! How many random rays to trace to make estimate?
n = 100

! Initialize the timer
TIMER

! Store the number of surfaces for later use
ns = NSUR()

! set the field coordinates here.
hx=0
hy=0

! get the chief ray offsets at the primary wavelength
px = 0
py = 0
RAYTRACE hx,hy,px,py,PWAV()
xc=RAYX(ns)
yc=RAYY(ns)


! Start at wavelength 1
weightsum=0
wwrms = 0
FOR w = 1, NWAV(), 1
	rms = 0
	FOR i = 1, n, 1
                angle = 6.283185 * RAND(1)
		! SQRT yields uniform distribution in pupil
                radius = SQRT(RAND(1))
                px = radius * COSI(angle)
                py = radius * SINE(angle)
                RAYTRACE hx,hy,px,py,w
                x=RAYX(ns)-xc
                y=RAYY(ns)-yc
                rms = rms + (x*x) + (y*y)
	NEXT
        rms = SQRT(rms/n)
        wwrms = wwrms + ( WWGT (w) * rms )
        weightsum = weightsum + WWGT(w)
        FORMAT .4
        PRINT "RMS spot size for ", WAVL(w),
        FORMAT .6
        PRINT " is ", rms
NEXT
wwrms = wwrms / weightsum
PRINT "Wavelength weighted rms is ", wwrms
FORMAT .2
t = ETIM()
PRINT "Elapsed time was ",t," seconds."
PRINT
