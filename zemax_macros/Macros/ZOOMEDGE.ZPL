! zoomedge.zpl
!
! Written by Kenneth E. Moore 8/92
!
! This macro computes the maximum aperture for each surface
! required to pass all rays in all zoom positions
! without vignetting. The non-zoomed semi-diameters
! will be reset to the maximum required aperture.
!
! The macro cannot alter, and will ignore, apertures
! which are already user-defined.
!
! After the semi-diameters are reset, the edge thickness for
! each surface in each zoom position is computed and displayed.
!
FORMAT .0
numconfig = NCON()
PRINT "There are ", numconfig, " zoom positions defined."
! start at first surface
sur = 0
LABEL 1
        sur = sur + 1
        max = 0
        config = 0
        LABEL 2
                config = config+1
                SETCONFIG config
                tem = SDIA(sur)
                IF (max < tem) THEN max = tem
                IF ( config < numconfig ) THEN GOTO 2
        FORMAT 3.0
        PRINT "The max semi-diameter of surface ", sur,
        FORMAT 8.4        
        PRINT " is ", max, 
        FORMAT 3.0
        PRINT " in configuration ", config
        SDIA sur = max
!        
! Now compute the edge thickness at each zoom position
!
        config = 0
        LABEL 3
                config = config+1
                SETCONFIG config
                tem = EDGE(sur)
                FORMAT 3.0
                PRINT "  Zoom ",config,": ",
                FORMAT 8.4
                PRINT "Edge thickness: ",tem
                IF ( config < numconfig ) THEN GOTO 3
        IF (sur < (NSUR()-1) ) THEN GOTO 1
PRINT
PRINT "All Done!"
