! This macro is intended to test out the PLOT2D keyword.
! The macro can be run with any ZEMAX file, as it does
! not use any data from the lens file.
!
! Written by S. Gangadhara, 06/24/08

! Set up an array to hold 2D data

nx = 100				# Number of X points
ny = 100				# Number of Y points
DECLARE xy_data, DOUBLE, 2, nx, ny	# 2D array of XY data points

! Fill the 2D array with a radially symmetric distribution

maxval = 5000.0				# Maximum value for the array
FOR i, 1, nx, 1
	FOR j, 1, ny, 1
		radsqr = (i - 0.5*nx)*(i - 0.5*nx) + (j - 0.5*ny)*(j - 0.5*ny)
		xy_data(i,j) = maxval - radsqr
	NEXT j
NEXT i

! Define settings for data plot

title$ = "Plot of XY data"		# Plot title
comment1$ = "This is a simple test"	# Plot comment line #1
comment2$ = "to determine if the"	# Plot comment line #2
comment3$ = "PLOT2D keyword is"		# Plot comment line #3
comment4$ = "working correctly"		# Plot comment line #4
comment5$ = "for all inputs."		# Plot comment line #5
rmin = 0.0				# Minimum plot value
rmax = maxval				# Maximum plot value
ratio = 1.0				# Plot aspect ratio
winrat = 0				# Window aspect ratio
actlft = -10.0				# Active cursor left value
actbot = -10.0				# Active cursor bottom value
actrgt = 10.0				# Active cursor right value
acttop = 10.0				# Active cursor top value
distyp = 5				# Display type
cnval$ = "900.0 2700.0 3400.0"		# Contour format
sscale = 0.75				# Surface scaling factor
lgpeak = 4				# Log plot peak value
lgdecd = 4				# Log plot decade value
lgtype = 0				# Log plot flag
addshow = 0				# Flag for whether to show address in plot
conshow = 0				# Flag for whether to show config number in plot

! Plot the data

PLOT2D NEW				# Initialize a new plot
PLOT2D TITLE, title$			# Place the title on the plot
PLOT2D COMM1, comment1$			# Place the comments on the plot
PLOT2D COMM2, comment2$
PLOT2D COMM3, comment3$
PLOT2D COMM4, comment4$
PLOT2D COMM5, comment5$
PLOT2D RANGE, rmin, rmax		# Define the data range to be plotted
PLOT2D ASPECT, ratio			# Define the x- to y-width plot ratio
PLOT2D WINASPECT, winrat		# Define the window aspect ratio
PLOT2D ACTIVECURSOR, actlft, actrgt, actbot, acttop	# Define values for the (x,y) corners of the plot
PLOT2D DISPLAYTYPE, distyp		# Define the data display type
IF (distyp == 1) THEN PLOT2D SURFACESCALE, sscale	# Define the surface scale factor (if necessary)
IF (distyp == 2) THEN PLOT2D CONTOURINTERVAL, cnval$	# Define the contour intervals  (if necessary)
IF (lgtype == 1)			# Convert the input data to a logarithmic scale (if necessary)
	FOR i, 1, nx, 1
		FOR j, 1, ny, 1
			xy_data(i,j) = LOGT(xy_data(i,j))
		NEXT j
	NEXT i
	PLOT2D LOGPLOT, lgpeak, lgdecd
ENDIF
PLOT2D HIDEADDRESS, addshow		# Define if address data will be shown in the window
PLOT2D CONFIG, conshow			# Define if config number will be shown in the window
PLOT2D DATA, xy_data			# Plot the data to a 2D plot using the defined display type
PLOT2D GO				# Generate the plot

! Release memory associated with array variable

RELEASE xy_data

! End program

PRINT "End of program."

END