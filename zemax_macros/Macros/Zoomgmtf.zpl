!
! ZOOMGMTF
!
! Written by Kenneth E. Moore 2-12-1997
! Extended by Kenneth E. Moore 1-21-1998
!
! This macro computes the geometric MTF at a specific spatial frequencies.
! Both the sine and square wave response are computed.
!
! The MTF is computed by integrating over all defined and non-zero weighted
! wavelengths in ALL zoom positions. This allows computation of the MTF
! across multiple configurations, such as in a 3 beam projector where
! the images are independently focusable and are recombined into a single image.
!
! It is assumed that all configurations have the same field data; no field weighting
! is considered. The reference point is the geometric centroid of all the rays.
!
! First define some useful constants:
!

ns = NSUR()
pi = 3.141592654
IF (UNIT() == 0) THEN uscale = 1.0
IF (UNIT() == 1) THEN uscale = 0.1
IF (UNIT() == 2) THEN uscale = 25.4
IF (UNIT() == 3) THEN uscale = 0.001

! The number of zoom positions
nzoom = NCON()

! The number of wavelengths
nwave = NWAV()

! The field position to use
INPUT "Enter field position number:", nfield
IF (nfield < 0) THEN nfield = 1
IF (nfield > NFLD()) THEN nfield = NFLD()

! The spatial frequency to use in lp/mm
INPUT "Enter spatial freq in lp/mm:", freq
IF (freq < 0) THEN freq = 0

! the sampling density to use (2n+1 x 2n+1 grid)
INPUT "Input grid size n (2n+1 X 2n+1 rays):", ngrid
ngrid = INTE(ngrid+.1)

! Now intialize the complex sum
tan_real = 0.0
tan_imag = 0.0
sag_real = 0.0
sag_imag = 0.0
rsum = 0.0

! we will also need the harmonics for the square wave computation
! Keep the first 7 harmonics

tan_real3 = 0.0
tan_imag3 = 0.0
sag_real3 = 0.0
sag_imag3 = 0.0

tan_real5 = 0.0
tan_imag5 = 0.0
sag_real5 = 0.0
sag_imag5 = 0.0

tan_real7 = 0.0
tan_imag7 = 0.0
sag_real7 = 0.0
sag_imag7 = 0.0

tan_real9 = 0.0
tan_imag9 = 0.0
sag_real9 = 0.0
sag_imag9 = 0.0

tan_real11 = 0.0
tan_imag11 = 0.0
sag_real11 = 0.0
sag_imag11 = 0.0

tan_real13 = 0.0
tan_imag13 = 0.0
sag_real13 = 0.0
sag_imag13 = 0.0

tan_real15 = 0.0
tan_imag15 = 0.0
sag_real15 = 0.0
sag_imag15 = 0.0

! more handy data; this converts the data to lp/mm no matter what the units are
freqfact    =  2.0 * pi * uscale * freq
freqfact3   =  3.0 * freqfact
freqfact5   =  5.0 * freqfact
freqfact7   =  7.0 * freqfact
freqfact9   =  9.0 * freqfact
freqfact11  = 11.0 * freqfact
freqfact13  = 13.0 * freqfact
freqfact15  = 15.0 * freqfact

! compute hx, hy for this field
! ASSUME this does not vary with zoom position!!!!!!!
!

maxfield = MAXF()
IF (maxfield > 0.0)
	hx = FLDX(nfield) / maxfield
	hy = FLDY(nfield) / maxfield
ELSE
	hx = 0.0
	hy = 0.0
ENDIF

! Trace the rays once to get the centroid position.
! Use about half the grid size; that should yield adequate accuracy
ngrid2 = INTE(0.5*ngrid+1)

refx = 0.0
refy = 0.0
rsum = 0.0

! Loop over the configurations
FOR c = 1, nzoom, 1
 SETCONFIG c
 UPDATE
 ! Loop over the wavelengths
 FOR w = 1, nwave, 1
  waveweight = WWGT(w)
  IF (waveweight == 0) THEN GOTO 1
  ! Loop over the x pupil
  FOR i = -ngrid2, ngrid2, 1
   px = i / ngrid2
   ! Loop over the y pupil
   FOR j = -ngrid2, ngrid2, 1
    py = j / ngrid2
    rad = px*px + py*py
    IF (rad <= 1.0)
     RAYTRACE hx, hy, px, py, w
     IF ((RAYE() == 0)&(RAYV() == 0))
      refx = refx + waveweight*RAYX(ns)
      refy = refy + waveweight*RAYY(ns)
      rsum = rsum + waveweight
     ENDIF
    ENDIF
   NEXT
  NEXT
  LABEL 1
 NEXT
NEXT

! Compute the reference coordinates
IF (rsum <= 0.0) THEN rsum = 0.0
refx = refx / rsum
refy = refy / rsum


! now trace more rays and compute the MTF and harmonics
! Loop over the configurations
rsum = 0.0
FOR c = 1, nzoom, 1
 SETCONFIG c
 UPDATE
 ! Loop over the wavelengths
 FOR w = 1, nwave, 1
  waveweight = WWGT(w)
  IF (waveweight == 0) THEN GOTO 2
  ! Loop over the x pupil
  FOR i = -ngrid, ngrid, 1
   px = i / ngrid
   ! Loop over the y pupil
   FOR j = -ngrid, ngrid, 1
    py = j / ngrid
    rad = px*px + py*py
    IF (rad <= 1.0)
     RAYTRACE hx, hy, px, py, w
     IF ((RAYE() == 0)&(RAYV() == 0))

      delx = freqfact*(RAYX(ns) - refx)
      dely = freqfact*(RAYY(ns) - refy)
      sag_real = sag_real + waveweight*COSI(delx);
      sag_imag = sag_imag + waveweight*SINE(delx);
      tan_real = tan_real + waveweight*COSI(dely);
      tan_imag = tan_imag + waveweight*SINE(dely);

      delx = freqfact3*(RAYX(ns) - refx)
      dely = freqfact3*(RAYY(ns) - refy)
      sag_real3 = sag_real3 + waveweight*COSI(delx);
      sag_imag3 = sag_imag3 + waveweight*SINE(delx);
      tan_real3 = tan_real3 + waveweight*COSI(dely);
      tan_imag3 = tan_imag3 + waveweight*SINE(dely);

      delx = freqfact5*(RAYX(ns) - refx)
      dely = freqfact5*(RAYY(ns) - refy)
      sag_real5 = sag_real5 + waveweight*COSI(delx);
      sag_imag5 = sag_imag5 + waveweight*SINE(delx);
      tan_real5 = tan_real5 + waveweight*COSI(dely);
      tan_imag5 = tan_imag5 + waveweight*SINE(dely);

      delx = freqfact7*(RAYX(ns) - refx)
      dely = freqfact7*(RAYY(ns) - refy)
      sag_real7 = sag_real7 + waveweight*COSI(delx);
      sag_imag7 = sag_imag7 + waveweight*SINE(delx);
      tan_real7 = tan_real7 + waveweight*COSI(dely);
      tan_imag7 = tan_imag7 + waveweight*SINE(dely);

      delx = freqfact9*(RAYX(ns) - refx)
      dely = freqfact9*(RAYY(ns) - refy)
      sag_real9 = sag_real9 + waveweight*COSI(delx);
      sag_imag9 = sag_imag9 + waveweight*SINE(delx);
      tan_real9 = tan_real9 + waveweight*COSI(dely);
      tan_imag9 = tan_imag9 + waveweight*SINE(dely);

      delx = freqfact11*(RAYX(ns) - refx)
      dely = freqfact11*(RAYY(ns) - refy)
      sag_real11 = sag_real11 + waveweight*COSI(delx);
      sag_imag11 = sag_imag11 + waveweight*SINE(delx);
      tan_real11 = tan_real11 + waveweight*COSI(dely);
      tan_imag11 = tan_imag11 + waveweight*SINE(dely);

      delx = freqfact13*(RAYX(ns) - refx)
      dely = freqfact13*(RAYY(ns) - refy)
      sag_real13 = sag_real13 + waveweight*COSI(delx);
      sag_imag13 = sag_imag13 + waveweight*SINE(delx);
      tan_real13 = tan_real13 + waveweight*COSI(dely);
      tan_imag13 = tan_imag13 + waveweight*SINE(dely);

      delx = freqfact15*(RAYX(ns) - refx)
      dely = freqfact15*(RAYY(ns) - refy)
      sag_real15 = sag_real15 + waveweight*COSI(delx);
      sag_imag15 = sag_imag15 + waveweight*SINE(delx);
      tan_real15 = tan_real15 + waveweight*COSI(dely);
      tan_imag15 = tan_imag15 + waveweight*SINE(dely);

      rsum = rsum + waveweight
     ENDIF
    ENDIF
   NEXT
  NEXT
  LABEL 2
 NEXT
NEXT

! Compute the modulous
IF (rsum <= 0.0) THEN rsum = 1.0
tan_mtf = tan_real*tan_real + tan_imag*tan_imag
sag_mtf = sag_real*sag_real + sag_imag*sag_imag
tan_mtf = SQRT(tan_mtf) / rsum
sag_mtf = SQRT(sag_mtf) / rsum

tan_mtf3 = tan_real3*tan_real3 + tan_imag3*tan_imag3
sag_mtf3 = sag_real3*sag_real3 + sag_imag3*sag_imag3
tan_mtf3 = SQRT(tan_mtf3) / rsum
sag_mtf3 = SQRT(sag_mtf3) / rsum

tan_mtf5 = tan_real5*tan_real5 + tan_imag5*tan_imag5
sag_mtf5 = sag_real5*sag_real5 + sag_imag5*sag_imag5
tan_mtf5 = SQRT(tan_mtf5) / rsum
sag_mtf5 = SQRT(sag_mtf5) / rsum

tan_mtf7 = tan_real7*tan_real7 + tan_imag7*tan_imag7
sag_mtf7 = sag_real7*sag_real7 + sag_imag7*sag_imag7
tan_mtf7 = SQRT(tan_mtf7) / rsum
sag_mtf7 = SQRT(sag_mtf7) / rsum

tan_mtf9 = tan_real9*tan_real9 + tan_imag9*tan_imag9
sag_mtf9 = sag_real9*sag_real9 + sag_imag9*sag_imag9
tan_mtf9 = SQRT(tan_mtf9) / rsum
sag_mtf9 = SQRT(sag_mtf9) / rsum

tan_mtf11 = tan_real11*tan_real11 + tan_imag11*tan_imag11
sag_mtf11 = sag_real11*sag_real11 + sag_imag11*sag_imag11
tan_mtf11 = SQRT(tan_mtf11) / rsum
sag_mtf11 = SQRT(sag_mtf11) / rsum

tan_mtf13 = tan_real13*tan_real13 + tan_imag13*tan_imag13
sag_mtf13 = sag_real13*sag_real13 + sag_imag13*sag_imag13
tan_mtf13 = SQRT(tan_mtf13) / rsum
sag_mtf13 = SQRT(sag_mtf13) / rsum

tan_mtf15 = tan_real15*tan_real15 + tan_imag15*tan_imag15
sag_mtf15 = sag_real15*sag_real15 + sag_imag15*sag_imag15
tan_mtf15 = SQRT(tan_mtf15) / rsum
sag_mtf15 = SQRT(sag_mtf15) / rsum

! Consider the diffraction limited MTF (optional)
! this code ignores chief ray tilt and pupil anamorphic shape
! it also ignores pupil and F/# changes with wavelength

lambda = WAVL(PWAV())
GETSYSTEMDATA 1
wfno = VEC1(10)

phi = 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf = tan_mtf*diff_mtf
sag_mtf = sag_mtf*diff_mtf
sw_diff_mtf = diff_mtf

phi = 3.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf3 = tan_mtf3*diff_mtf
sag_mtf3 = sag_mtf3*diff_mtf
sw_diff_mtf = sw_diff_mtf - diff_mtf/3

phi = 5.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf5 = tan_mtf5*diff_mtf
sag_mtf5 = sag_mtf5*diff_mtf
sw_diff_mtf = sw_diff_mtf + diff_mtf/5

phi = 7.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf7 = tan_mtf7*diff_mtf
sag_mtf7 = sag_mtf7*diff_mtf
sw_diff_mtf = sw_diff_mtf - diff_mtf/7

phi = 9.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf9 = tan_mtf9*diff_mtf
sag_mtf9 = sag_mtf9*diff_mtf
sw_diff_mtf = sw_diff_mtf + diff_mtf/9

phi = 11.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf11 = tan_mtf11*diff_mtf
sag_mtf11 = sag_mtf11*diff_mtf
sw_diff_mtf = sw_diff_mtf - diff_mtf/11

phi = 13.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf13 = tan_mtf13*diff_mtf
sag_mtf13 = sag_mtf13*diff_mtf
sw_diff_mtf = sw_diff_mtf + diff_mtf/13

phi = 15.0 * 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))
tan_mtf15 = tan_mtf15*diff_mtf
sag_mtf15 = sag_mtf15*diff_mtf
sw_diff_mtf = sw_diff_mtf - diff_mtf/15

! compute the SW MTF
tan_sw_mtf = tan_mtf - tan_mtf3/3.0 + tan_mtf5/5.0 - tan_mtf7/7.0 + tan_mtf9/9.0
tan_sw_mtf = tan_sw_mtf - tan_mtf11/11.0 + tan_mtf13/13.0 - tan_mtf15/15.0
tan_sw_mtf = 4.0*tan_sw_mtf/pi

sag_sw_mtf = sag_mtf - sag_mtf3/3.0 + sag_mtf5/5.0 - sag_mtf7/7.0 + sag_mtf9/9.0
sag_sw_mtf = sag_sw_mtf - sag_mtf11/11.0 + sag_mtf13/13.0 - sag_mtf15/15.0
sag_sw_mtf = 4.0*sag_sw_mtf/pi

sw_diff_mtf = 4.0*sw_diff_mtf/pi

! compute again the sine wave diff limit
phi = 0.001 * lambda * wfno * freq
IF (phi > 1.0) THEN phi = 1.0;
phi = ACOS(phi)
diff_mtf = (2.0 / pi) * (phi - COSI(phi)*SINE(phi))

! Print out the results

FORMAT 3.0

PRINT
PRINT "Grid size: ", 2*ngrid+1, " X ", 2*ngrid+1
PRINT "# of configurations: ", nzoom
PRINT "# of wavelengths: ", nwave
PRINT "Field position: ", nfield

FORMAT 12.4

PRINT
PRINT "Reference X coordinate: ", refx
PRINT "Reference Y coordinate: ", refy
PRINT
PRINT "Sine wave response:"
PRINT
PRINT "   Frequency  Tangential    Sagittal  Diff Limit"
PRINT freq,  tan_mtf, sag_mtf, diff_mtf
PRINT
PRINT "Square wave response:"
PRINT
PRINT "   Frequency  Tangential    Sagittal  Diff Limit"
PRINT freq,  tan_sw_mtf, sag_sw_mtf, sw_diff_mtf
