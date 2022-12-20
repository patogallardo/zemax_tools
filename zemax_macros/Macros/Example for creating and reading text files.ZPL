! This macro sample demonstrates the use of the GETTEXTFILE, OPEN, CLOSE, DELETEFILE, and 
! READSTRING ZPL keywords, the SVAL function, and the and $GETSTRING string function.
! 
! Written by Kenneth E. Moore 12-15-03
!
! Get a temporary file name
A$ = $TEMPFILENAME()

! Compute the data and place in the temp file
GETTEXTFILE A$, Car

! Print a header with the file name
PRINT "Cardinal Point Data now stored in file ", A$

! Open the new file
OPEN A$

! Create a loop to read and print the entire file
LABEL 1
READSTRING B$
IF (EOFF()) THEN GOTO 2
PRINT B$
GOTO 1
LABEL 2
CLOSE

! Suppose we just want the wavelength.

! Open the new file again.
OPEN A$
LABEL 3

! read the lines one at a time.
READSTRING B$
IF (EOFF()) THEN GOTO 4

! Get the first string on the line
C$ = $GETSTRING(B$, 1)

! Does the first string say "Wavelength"? If not jump to 3 and keep reading.
IF (C$ $!= "Wavelength") THEN GOTO 3

! Found it! Print the whole line for reference. Note the wavelength is string #3.
PRINT B$

! Get the third string.
C$ = $GETSTRING(B$, 3)

! Convert to a numerical value
W = SVAL(C$)

! Print it out
PRINT "Wavelength is: ", W

! clean up
LABEL 4
CLOSE

! Clean up by deleting the temporary file
DELETEFILE A$
