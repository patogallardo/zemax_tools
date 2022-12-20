! Macros FIFTHORD and ZPL03
! Routines to calculate the third- and fifth-order coefficients of a centered optical system
! containing spherical and even-order aspheric surfaces.  These macros were developed from the work
! of Rimmer (1962, University of Rochester Summer School in Optics).  The routine has also been 
! shaped by exposure to a FORTRAN subroutine named FORD which someone from Kitt Peak gave me many 
! years ago.  The macro also is also similar to the Code V macro Fifthdef which was, I believe, also
! written by Rimmer.  No claim to originality is made for this macro but I believe it to be 
! substantially correct as far as it goes.  
!
! The macro calculates the third- and fifth-order coefficients along with the coefficient of 
! seventh-order spherical aberration. The coefficients are those of the transverse aberration, 
! being the unconverted coefficients multiplied by the F/ number of the system.  To print
! the unconverted coefficients, eliminate the three lines of code just above the final print 
! block.  
!
! The coefficients that are calculated are given here and explained in the reference above and in
! Buchdahl "Optical Aberrations Coefficients", Dover, 1958 (See sections 31, 203, 218).		
! The OPTRETURN number for the optimization version (ZPL03.zpl) is given to the right:
!
!	B	Third-order spherical aberration	OPTRETURN 0	
!	F	Third-order saggital coma 		OPTRETURN 1	
!	C	Third-order astigmatism			OPTRETURN 2	
!	Pi	Petzval sum (Field curvature)		OPTRETURN 3		
!	E	Third-order distortion			OPTRETURN 4	
!	B5	Fifth-order spherical aberration	OPTRETURN 5	
!	F1	Fifth-order coma			OPTRETURN 6
!	F2	Fifth-order coma			OPTRETURN 7	
!	M1	Oblique spherical aberration		OPTRETURN 8	
!	M2	Oblique spherical aberration		OPTRETURN 9	
!	M3	Oblique spherical aberration		OPTRETURN 10	
!	N1	Elliptical coma				OPTRETURN 11
!	N2	Elliptical coma				OPTRETURN 12	
!	N3	Elliptical coma				OPTRETURN 13
!	C5	Fifth-order astigmatism			OPTRETURN 14	
!	Pi5	Fifth-order Petzval (Field curvature)	OPTRETURN 15
!	E5	Fifth-order distortion			OPTRETURN 16	
!	B7	Seventh-order spherical aberration	OPTRETURN 17	
!
! The macro will request a wavelength for the calculations.  The wavelength number will be printed
! along with the coefficients. This is not true of the optimization version (ZPL03.zpl).  Here, just
! the principal wavelength is used.
!
! General comment:  The fifth-order coefficients are not used nearly as much as they used to be now
! that ray tracing is so fast and convenient.  This macro is mainly for old-timers like me who want 
! to continue the dream that they still maintain some control over and understanding of the design 
! process.  When tracing a million ray surfaces a second is common, these coefficients are of 
! questionable value.  One final comment: Zemax uses a second-order aspheric deformation coefficient
! which is not used in this treatment.  It may appear in a future version.
! Good luck with the macro if you are brave (or foolish) enough to use it.
!
!                                                         M. MacFarlane
!                                                         March, 1998
!
! Modified to account for sign chnage on index in mirror spaces 5-20-2003, thanks to T. A. Mitchell

paraxmode = PMOD()

PARAXIAL ON
wl = PWAV()
ns = NSUR()
nsm = ns - 1
RAYTRACE 0, 0, 0, 1, wl
py = RAYY(1)
pu = RAYM(1) / RAYN(1)
pup = RAYM(nsm) / RAYN(nsm)
fnum = -0.5 / Indx(nsm) / pup
RAYTRACE 0, 1, 0, 0, wl
pyc = RAYY(1)
puc = RAYM(1) / RAYN(1)
Lagrange = INDX(1) * (py * puc - pu * pyc)
eps = 1e-10

FOR nab = 1, 23, 1
   vec1(nab) = 0
NEXT

PRINT " "
PRINT " "
PRINT "Unconverted Buchdahl Coefficients"

FOR i = 1, nsm, 1
   cv = CURV(i)
   index = INDX(i-1)
   indexp = INDX(i)

   ! Account for mirrors
   if ISMS(i-1) then index = -index
   if ISMS(i) then indexp = -indexp
   ! T.A. Mitchell, 04/17/03

   k = index / indexp
   km1 = k - 1
   deln = index - indexp
   RAYTRACE 0, 0, 0, 1, wl
   py = RAYY(i)
   pu = RAYM(i-1) / RAYN(i-1)
   pup = RAYM(i) / RAYN(i)
   pai = cv * py + pu
   paip = pai * k
   RAYTRACE 0, 1, 0, 0, wl
   pyc = RAYY(i)
   puc = RAYM(i-1) / RAYN(i-1)
   pucp = RAYM(i) / RAYN(i)
   paic = cv * pyc + puc
   paicp = paic * k

   ! Third-order spherical contributions

   P = cv * km1 * Lagrange * Lagrange / index
   Sa = index * km1 * py * (pai + pup)
   Sb = index * km1 * pyc * (paic + pucp)
   Ba = Sa * pai * pai
   Fa = Sa * pai * paic
   Ca = Sa * paic * paic
   Bb = Sb * paic * paic
   Fb = Sb * pai * paic
   Cb = Sb * pai * pai
   Ea = Fb + Lagrange * km1 * paic * (pucp + puc)
   Eb = Fa - Lagrange * km1 * pai * (pup + pu)

   ! Intrinsic fifth-order spherical contributions

   w = (pai * pai + paip * paip + pup * pup - 3 * pu * pu)/8
   x73 = 3 * pai * paip + 2 * pup * pup - 3 * pu * pu
   x74 = 3 * pai * paicp + 2 * pup * pucp - 3 * pu * puc
   x75 = 3 * paic * paicp + 2 * pucp * pucp - 3 * puc * puc
   x76 = pai * (3 * pu - pup)
   x77 = paic * (2 * pu - pup) + pai * puc 
   x78 = paic * (3 * puc - pucp)   
   x42 = pyc * pai * (paic - puc) + py * paic * (pucp + puc)
   x82 = pyc * pu * (paic - puc) - py * paicp * (pucp + puc)
   x42b = py * paic * (pai - pu) + pyc * pai * (pup + pu)
   x82b = py * puc * (pai - pu) - pyc * paip * (pup + pu)
   S1p = 3 * w * Sa * pai
   S2p = Sa * (paic * x73 + pai * x74 - pucp * x76 - pup * x77) / 4
   S3p = index * km1 * (x42 * x73 + x76 * x82 + py * (pai + pup) * (pai * x75 - pup * x78)) / 4
   S4p = Sa * (paic * x74 - pucp * x77)
   S5p = index * km1 * (x42 * x74 + x77 * x82 + py * (pai + pup) * (paic * x75 - pucp * x78)) / 4
   S6p = index * km1 * (x42 * x75 + x78 * x82) / 4
   S1q = index * km1 * (x42b * x73 + x76 * x82b) / 4
   t1p = 10 * w * w + Sa * pai * cv * (2 * pup - 5 * pu) / index / 8
   B5 = pai * S1p
   F1 = paic * S1p + pai * S2p
   F2 = pai * S2p
   M1 = 2 * paic * S2p
   M2 = pai * S3p
   M3 = pai * S4p
   N1 = paic * S3p
   N2 = paic * S4p + 2 * pai * S5p
   N3 = pai * s5p
   C5 = 0.5 * paic * S5p
   P5 = pai * S6p - .5 * paic * S5p
   E5 = paic * S6p
   E5b = pai * S1q
   B7 = Ba * t1p

   asphere = 0

   IF abso(coni(i)) > eps 
      conic = coni(i)
      aterm = 0
      bterm = 0
      cterm = 0
      asphere = 1
   ENDIF
   
   IF abso(styp(i) - scod("EVENASPH")) < eps
      conic = coni(i)
      aterm = par2(i)
      bterm = par3(i)
      cterm = par4(i)
      asphere = 1
   ENDIF

   ! Intrinsic third- and fifth-order aspheric contributions

   IF asphere
      cv2 = cv * cv
      cv3 = cv2 * cv
      c1 = 8 * aterm + conic * cv3
      c2 = 12 * bterm + .75 * cv2 * (cv3 * conic * (conic + 2) - 2 * c1)
      temp = cv3 * conic * (conic * conic + 3 * conic +3) - 3 * c1
      temp = cv2 * (5 * cv2 * temp - 12 * c2)
      temp = (-6 * cv * c1 * c1 + temp) / 8
      c3 = 16 * cterm + temp
      c1b = deln * c1
      c2b = deln * c2
      c3b = deln * c3
      pysq = py * py
      pycsq = pyc * pyc
      aBa = c1b * pysq * pysq
      aFa = c1b * pysq * py * pyc
      aEb = aFa
      aCa = c1b * pysq * pycsq
      aCb = aCa
      aEa = c1b * py * pycsq * pyc
      aFb = aEa
      aBb = c1b * pycsq * pycsq
      Ba = Ba + aBa
      Fa = Fa + aFa
      Ca = Ca + aCa
      Ea = Ea + aEa
      Bb = Bb + aBb
      Fb = Fb + aFb
      Cb = Cb + aCb
      Eb = Eb + aEb
      mm = k * Lagrange / indexp
      la = (3 * paip - 2 * (1 - 2 * k) * pup) / 4
      lb = (3 * paicp - 2 * (1 - 2 * k) * pucp) / 4
      aS1p1 = aBa * la
      aS2p1 = 2 * aFa * la + .5 * c1b * pysq * py * mm
      aS3p1 = 2 * aCa * la + c1b * pysq * pyc * mm
      aS4p1 = 2 * aS3p1
      aS5p1 = 2 * aEa * la + 1.5 * c1b * py * pycsq * mm
      aS6p1 = aBb * la + c1b * pycsq * pyc * mm
      aS1q1 = aBa * lb - c1b * pysq * py * mm
      j0a = c2b * py - .25 * cv * c1b * (3 * paip - 5 * pup)
      j0b = c2b * pyc - .25 * cv * c1b * (3 * paicp - 5 * pucp)
      alpha = .5 * (pup * (pup - pai) + pai * (3 * paip - pup))
      beta = pup * (pucp - paic) + pai * (3 * paicp - pucp)
      gamma = .5 * (pucp * (pucp - paic) + paic * (3 * paicp - pucp))
      lambda = alpha * c1b + j0a * py
      mu = beta * c1b + 2 * j0a * pyc
      nu = py * gamma * c1b + j0a * pycsq 
      aS1p2 = pysq * py * lambda
      aS2p2 = pysq * pyc * lambda + .5 * pysq * py * mu
      aS3p2 = py * pycsq * lambda + pysq * nu
      aS4p2 = 2 * pysq * pyc * mu
      aS5p2 = .5 * py * pycsq * mu + py * pyc * nu
      aS6p2 = pycsq * nu
      aS1q2 = pysq * (alpha * c1b * pyc + j0b * pysq)
      aS1pa = pai * aS1p1 + py * aS1p2
      aS2pa = pai * aS2p1 + py * aS2p2    
      aS3pa = pai * aS3p1 + py * aS3p2
      aS4pa = pai * aS4p1 + py * aS4p2
      aS5pa = pai * aS5p1 + py * aS5p2    
      aS6pa = pai * aS6p1 + py * aS6p2
      aS1pb = paic * aS1p1 + pyc * aS1p2
      aS2pb = paic * aS2p1 + pyc * aS2p2    
      aS3pb = paic * aS3p1 + pyc * aS3p2
      aS4pb = paic * aS4p1 + pyc * aS4p2
      aS5pb = paic * aS5p1 + pyc * aS5p2    
      aS6pb = paic * aS6p1 + pyc * aS6p2
      aS1qa = pai * aS1q1 + py * aS1q2
      aB5 = aS1pa
      aF1 = aS1pb + aS2pa
      aF2 = aS2pa
      aM1 = 2 * aS2pb
      aM2 = aS3pa
      aM3 = aS4pa
      aN1 = aS3pb
      aN2 = aS4pb + 2 * aS5pa
      aN3 = aS5pa
      aC5 = .5 * aS5pb
      aP5 = aS6pa - .5 * aS5pb
      aE5 = aS6pb
      aE5b = aS1qa
      B5 = B5 + aB5
      F1 = F1 + aF1
      F2 = F2 + aF2
      M1 = M1 + aM1
      M2 = M2 + aM2
      M3 = M3 + aM3
      N1 = N1 + aN1
      N2 = N2 + aN2
      N3 = N3 + aN3
      C5 = C5 + aC5
      P5 = P5 + aP5
      E5 = E5 + aE5
      E5b = E5b + aE5b
      gamma1 = c1 * pysq
      gamma2 = py * pysq * (c2 * py + .25 * cv * c1 * (pai + 3 * pu))
      temp = cv2 * c1 * (pai * (pai + 5 * pu) - pu * (pai - 5 * pu)) / 8
      temp = temp + c1 * c1 * py * pai / 4
      gamma3 = pysq * pysq * (temp + c3 * pysq + (1/3) * cv * c2 * py * (pai + 5 * pu))
      d3 = cv * py * (4 * cv * py * (pai + pu ) + paip * (5 * (2 * pup + pai) + paip))
      temp = k * pup * (3 * pai * pai - 10 * pu * pu + paip * (4 * (2 * pup + paip + pai) + pai))
      d3 = c1 * (gamma1 * py * (1 + 2 * k * km1) + d3 + temp) / 8
      d3 = deln * pysq * pysq * ((1/6) * c2 * pysq * (4 * paip + 3 * pup * (2 * k - 1)) + d3)
      L3 = py * gamma3 * deln + .5 * (gamma1 * (S1p + aS1p1) + gamma2 * Sa * pai)  
      aB7 = pai * d3 + py * L3
      B7 = B7 + aB7
      
   ENDIF

   ! Total fifth order aberration coefficients

   temp = .5 * vec1(1) * vec1(1) * (p + 3 * Ca)/ Lagrange
   temp = temp + 3 * (vec1(10) - vec1(1) * vec1(9) / Lagrange) * Fa
   temp = temp + 3 * (.5 * vec1(9) * vec1(9) / Lagrange - vec1(22))* Ba
   temp = (temp + vec1(1) * (F1 + F2) - 5 * vec1(9) * B5) / (2 * Lagrange)
   B7 = B7 + temp
   B5 = B5 + 1.5 * (vec1(1) * Fa - vec1(9) * Ba) / Lagrange
   temp = vec1(1) * (p + 4 * Ca) + (5 * vec1(2) - 4 * vec1(9)) * Fa - (2 * vec1(5) + 5 * vec1(8)) * Ba
   F1 = F1 + temp / (2 * Lagrange)
   temp = vec1(1) * (P + 2 * Ca) + 2 * (2 * vec1(2) - vec1(9)) * Fa - (vec1(5) + 4 * vec1(8)) * Ba
   F2 = F2 + temp / (2 * Lagrange)
   temp = vec1(1) * Ea + (4 * vec1(2) - vec1(9)) * Ca - vec1(7) * Ba 
   temp = temp + (vec1(3) - 4 * vec1(8) - 2 * vec1(5)) * Fa
   M1 = M1 + temp / Lagrange
   temp = vec1(1) * Ea + (2 * vec1(2) - vec1(9)) * (P + Ca) + (3 * vec1(3) - 2 * vec1(8) + vec1(5)) * Fa - 3 * vec1(7) * Ba
   M2 = M2 + temp / (2 * Lagrange)
   temp = vec1(2) * (P + 2 * Ca) - vec1(7) * Ba + (vec1(3) - 2 * vec1(8)) * Fa
   M3 = M3 + 2 * temp / Lagrange
   temp = 3 * vec1(2) * Ea - (vec1(5) + vec1(8)) * (P + Ca) + 2 * (vec1(3) - vec1(8)) * Ca    
   temp = temp + (vec1(4) - 2 * vec1(7)) * Fa - vec1(6) * Ba
   N1 = N1 + temp / (2 * Lagrange)
   temp = 3 * vec1(2) * Ea + (vec1(5) - vec1(8) + 3 * vec1(3)) * (p + 3 * Ca)
   temp = temp - vec1(6) * Ba - (vec1(5) + vec1(3)) * Ca + (vec1(4) - 8 * vec1(7)) * Fa
   N2 = N2 + temp / Lagrange
   temp = vec1(2) * Ea + (3 * vec1(3) + vec1(5) - vec1(8)) * (P + Ca) - vec1(6) * Ba
   temp = temp + (vec1(5) + vec1(3)) * Ca + (vec1(4) - 4 * vec1(7)) * Fa
   N3 = N3 + temp / (2 * Lagrange)
   temp = (4 * vec1(3) + vec1(5)) * Ea - vec1(7) * P + 2 * (vec1(4) - 2 * vec1(7)) * Ca
   temp = temp - 2 * vec1(6) * Fa
   C5 = C5 + temp / (4 * Lagrange)
   temp = (vec1(5) - 2 * vec1(3)) * Ea + (4 * vec1(4) - vec1(7)) * P 
   temp = temp - 2 * vec1(6) * Fa + 2 * (vec1(4) + vec1(7)) * Ca
   P5 = P5 + temp / (4 * Lagrange)
   E5 = E5 + (3 * vec1(4) * Ea - vec1(6) * (P + 3 * Ca)) / (2 * Lagrange)
   E5b = E5b + (vec1(1) * (P + 3 * Cb) - 3 * vec1(9) * Eb) / (2 * Lagrange)

   vec1(1) = vec1(1) + Ba  
   vec1(2) = vec1(2) + Fa  
   vec1(3) = vec1(3) + Ca 
   vec1(4) = vec1(4) + Ea 
   vec1(5) = vec1(5) + P 
   vec1(6) = vec1(6) + Bb 
   vec1(7) = vec1(7) + Fb 
   vec1(8) = vec1(8) + Cb 
   vec1(9) = vec1(9) + Eb 
   vec1(10) = vec1(10) + B5 
   vec1(11) = vec1(11) + F1 
   vec1(12) = vec1(12) + F2 
   vec1(13) = vec1(13) + M1 
   vec1(14) = vec1(14) + M2 
   vec1(15) = vec1(15) + M3
   vec1(16) = vec1(16) + N1
   vec1(17) = vec1(17) + N2
   vec1(18) = vec1(18) + N3
   vec1(19) = vec1(19) + C5
   vec1(20) = vec1(20) + P5
   vec1(21) = vec1(21) + E5
   vec1(22) = vec1(22) + E5b
   vec1(23) = vec1(23) + B7

NEXT 


FOR nab = 1, 23, 1
   vec1(nab) = vec1(nab) * fnum
NEXT

OPTRETURN 0 = vec1(1)
OPTRETURN 1 = vec1(2)
OPTRETURN 2 = vec1(3)
OPTRETURN 3 = vec1(5)
OPTRETURN 4 = vec1(4)
OPTRETURN 5 = vec1(10)
OPTRETURN 6 = vec1(11)
OPTRETURN 7 = vec1(12)
OPTRETURN 8 = vec1(13)
OPTRETURN 9 = vec1(14)
OPTRETURN 10 = vec1(15)
OPTRETURN 11 = vec1(16)
OPTRETURN 12 = vec1(17)
OPTRETURN 13 = vec1(18)
OPTRETURN 14 = vec1(19)
OPTRETURN 15 = vec1(20)
OPTRETURN 16 = vec1(21)
OPTRETURN 17 = vec1(23)

IF abso(paraxmode) < eps THEN PARAXIAL OFF


