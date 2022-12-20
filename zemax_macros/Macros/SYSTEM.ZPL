! system.zpl
! 
! This macro demonstrates the GETSYSTEMDATA command.
!
! Written by K. Moore 11-1-94
!
FORMAT 12.5
GETSYSTEMDATA 1
PRINT "Number of entries    : ", VEC1(0)
PRINT "Aperture Value       : ", VEC1(1)
PRINT "Apodization Factor   : ", VEC1(2)
PRINT "Apodization Type     : ", VEC1(3)

PRINT "Use Env Data         : ", VEC1(4)
PRINT "Temp (C)             : ", VEC1(5)
PRINT "Pressure (ATM)       : ", VEC1(6)

PRINT "EFL                  : ", VEC1(7)
PRINT "Image Space F/#      : ", VEC1(8)
PRINT "Object Space N.A.    : ", VEC1(9)
PRINT "Working F/#          : ", VEC1(10)

PRINT "Entrance Pupil Dia   : ", VEC1(11)
PRINT "Entrance Pupil Pos   : ", VEC1(12)
PRINT "Exit Pupil Dia       : ", VEC1(13)
PRINT "Exit Pupil Pos       : ", VEC1(14)

PRINT "Parax Image Height   : ", VEC1(15)
PRINT "Parax Magnification  : ", VEC1(16)
PRINT "Angular Magnification: ", VEC1(17)

PRINT "Total Track          : ", VEC1(18)

PRINT "Use Ray Aiming       : ", VEC1(19)
PRINT "X Pupil Shift        : ", VEC1(20)
PRINT "Y Pupil Shift        : ", VEC1(21)
PRINT "Z Pupil Shift        : ", VEC1(22)
PRINT "Stop Surface Number  : ", VEC1(23)
