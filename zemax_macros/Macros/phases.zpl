! phases.zpl
!
! Written by Mary G.Turner 11 Apr 96
!
!
PRINT "This program computes the radii of the"
PRINT "different steps on a binary 2 surface " 
PRINT "resulting in 2*m*pi phase shifts"
PRINT
PRINT "Cycles (m)           ","radius       "

OUTPUT SCREEN
!Get user information
INPUT "Which surface (must be surface type binary 2)?", h

! Retrieve the coefficients and normalized radius from 
! the extra data editor


GETEXTRADATA 1,h
normrad = VEC1(2)
                 ! Normalized pupil radius
steps = VEC1(1) 
                 ! Number of terms in expansion 

! Necessary constant
pi = 2 * ACOS(0)
pi2 = 2 * pi

! Initializations  

deltamin = normrad
oldradius = 0
baseradius = 0              
rhobase = 0
rhohold = 0
rhomax = 1
delta = 10
phi = 0
phislope = 0
FOR j = 1 , steps , 1
    phislope = phislope + VEC1(j+2)*POWR(.01,(2*j))
NEXT 
     
LABEL 1  
          ! Initialize for each attempt 
          FLAG = 0
          phase = 0 
          phaseplus = 0
          phaseminus = 0

          IF rhobase > 0.9999 THEN GOTO 3

          rho = rhobase + (rhomax - rhobase)/delta 
         ! Calculate the phase at this radius
                                          
          FOR j = 1 , steps , 1
              phase = phase + VEC1(j+2)*POWR(rho,(2*j))
              phaseplus = phaseplus + VEC1(j+2)*POWR(rho+.005,(2*j))
              phaseminus = phaseminus + VEC1(j+2)*POWR(rho-.005,(2*j))
          NEXT 

         IF phase < 0.00 THEN FLAG = 1
         slope = phaseplus - phaseminus 

         ! Check to see if desired phase change
         IF (ABSO( pi2 - ABSO(phase - phi)) <= 0.00001 ) 
             GOTO 2
   
         ! Need to adjust and try again
         ELSE
             IF ((ABSO(phase - phi) < pi2)) THEN rhobase = rho      
                                                    ! Not there yet
             IF ((ABSO(Phase - phi) > pi2)) THEN rhomax  = rho 
                                                    ! Went too far
         ENDIF           
                 
         GOTO 1

LABEL 2  
         IF ((slope*phislope)> 0) 
            ! Found the next location 
            GOTO 4

         ! Missed a value near an inflection point
         ELSE 
            rhobase = rhohold
            rhomax = rho - (rho - rhobase)/ 100
LABEL 6
            rho = rhobase + (rhomax - rhobase)/delta 
            phase = 0
            FOR j = 1 , steps , 1
              phase = phase + VEC1(j+2)*POWR(rho,(2*j))
            NEXT

            ! Check to see if desired phase change
            IF (ABSO(phase - phi)  <= 0.00001 )
               GOTO 4
            ! Need to adjust and try again
            ELSE
               IF ( slope > 0 ) 
                  IF ((phase - phi) > 0 )
                      rhomax = rho
                  ELSE
                      rhobase = rho
                  ENDIF
               ELSE
                  IF ((phase - phi) < 0 )
                      rhomax = rho
                  ELSE
                      rhobase = rho
                  ENDIF
               ENDIF
            ENDIF
         ENDIF 
         GOTO 6
LABEL 4          
         ! Met the requirements
             
             Radius = rho * normrad
             Order = phase/pi2
             Order = ABSO(Order) + .1
             Order = INTE(Order) 
             IF (FLAG) THEN Order = -1 * Order
             FORMAT 10.6
             PRINT   order, "       ", radius 

             ! Find minimum radial change
             deltarad = radius - oldradius
             IF deltarad < deltamin
                deltamin = deltarad
                baseradius = oldradius
             ENDIF
              
            ! Prepare for next cycle
             oldradius = radius 
             rhobase = rho 
             rhohold = rho
             rhomax = 1
             phi = phase 
             phislope = slope
             delta = 10
    GOTO 1
         ! Calculate next cycle
END

LABEL 3
         PRINT "Reached edge of surface."
PRINT "The minimum radial change was ", deltamin," which occured after radius of ", baseradius      

! The End
PRINT "All Done!"           
