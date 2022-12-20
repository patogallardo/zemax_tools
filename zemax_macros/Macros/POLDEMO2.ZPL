! poldemo2
!
! Written by Kenneth E. Moore 1-5-96
!
! This macro launches many random rays from a square object field, and averages
! the electric field to give an indication of the average polarization state.
!

! First, define the input polarization:
! The arguments to POLDEFINE are Ex, Ey, PhaseX, Phase Y
!
POLDEFINE 0.0, 1.0, 0.0, 0.0

! Define the number of rays
numray = 100

! Define the surface at which we compute data
ns = NSUR()

! Define the wavelength number
w = 1

! The size of the object is given by the field definitions.
! We will choose rays that lie within a square defined by hx = { -.707, .707 }
! and hy = { -.707, .707 }
norm = SQRT(2.0)

! initialize the averages
exr = 0.0
eyr = 0.0
exi = 0.0
eyi = 0.0
tot = 0.0

! how many rays have we traced so far?
n = 0

! define a counter for bad rays
bad = 0

! here is where we will loop
LABEL 1


! Pick a random field coordinate
hx = RAND(norm) - 0.5 * norm
hy = RAND(norm) - 0.5 * norm

! Pick a random pupil coordinate
angle = 6.283185 * RAND(1)
radius = SQRT(RAND(1))
px = radius * COSI(angle)
py = radius * SINE(angle)

! trace the ray and put the data in vector 1
POLTRACE hx, hy, px, py, w, 1, ns

! See if any errors occured
IF (VEC1(0) > 0)
	! Ok, valid data

	!  Increment the counter
	n = n + 1

	! Extract the data
	int = VEC1(1)
	amp = SQRT(int)
	tot = tot + int
	exr = exr + amp*VEC1(2)
	exi = exi + amp*VEC1(5)
	eyr = eyr + amp*VEC1(3)
	eyi = eyi + amp*VEC1(6)
ELSE
	! keep track of how many rays fail to trace
	bad = bad + 1
ENDIF


! If there are too many bad rays, this will avoid an infinte loop
IF (bad > 100)
	PRINT "Too many bad rays!"
	GOTO 2
ENDIF

IF (n < numray) THEN GOTO 1

! to get here, we must have enough good data!
IF (n > 0)
	exr = exr / n
	exi = exi / n
	eyr = eyr / n
	eyi = eyi / n
	tot = tot / n
ENDIF

ext = SQRT(exr*exr + exi*exi)
eyt = SQRT(eyr*eyr + eyi*eyi)

! If the output is unpolarized, the average of all rays will be small...
! if perfectly polarized, then the dop will be unity
! the dop is normalized to the total transmission */

dop = 0.0
IF (tot > 0) THEN dop = (ext*ext + eyt*eyt) / (tot*tot)

! Print something!
PRINT "Degree of polarization: ", dop

LABEL 2
