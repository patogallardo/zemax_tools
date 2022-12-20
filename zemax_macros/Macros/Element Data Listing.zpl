!Elemdata.zpl
!Calculate the paraxial data of every element made of glass
!Convenient for lens drawing and manufactoring
!Programed by Nong Wen Jie &Jin Ning of Kumming Institude of Physics,China 
!If you have any comment or requirment please mail to sanyuesan@sina.com

PRINT
PRINT
PRINT "Elemdata.zpl"
PRINT "Calculate the paraxial data of every element made of glass, assuming the element is immeresed in air"
PRINT "Convenient for lens drawing and manufacture"
PRINT "Programed by Nong Wen Jie of Kumming Institude of Physics,China"
PRINT "If you have any comment or requirement please mail to sanyuesan@sina.com"

PRINT  
FILE$  = $FILEPATH()
TITLE$ = $LENSNAME()
PRINT "File : ", FILE$
PRINT "Title: ", TITLE$
PRINT

PRINT
PRINT "Calculate element paraxial data:"
PRINT "LH and LH' : principal planes position"
PRINT "l and l' : front focal length and back focal length"
PRINT "EFFL : effective focal length"
PRINT "Power : element power"
PRINT "LH and l are measured with respect to first surface of element"
PRINT "LH' and l' are measured with respect to second surface of element"
PRINT 
PRINT

PRINT "ELEM(S1-S2)         LH          LH'          EFFL          l          l'            Power"
FOR N=1,NSUR(),1
IF (INDX(N)!=1)&(THIC(N)!=0)
	FORMAT 2.0
	PRINT "(",N,"-",N+1,")",
	FORMAT 14.6
	
	IF (RADI(N) == 0.0) & (RADI(N+1) == 0.0)
		PRINT "     Undefined",
		PRINT "     Undefined",
		PRINT "      Infinity",
		PRINT "      Infinity",
		PRINT "      Infinity",
		PRINT 0.0
	ELSE
		!Calculate LH and LH' and print it
		
		IF (RADI(N) == 0.0) & (RADI(N+1) != 0.0)   
			LH = THIC(N)/INDX(N)
			LHP = 0.0
		ENDIF

		IF (RADI(N) != 0.0) & (RADI(N+1) == 0.0)
			LH = 0.0
			LHP = -THIC(N)/INDX(N)
		ENDIF

		IF (RADI(N) != 0.0) & (RADI(N+1) != 0.0)
			LH=-1*RADI(N)*THIC(N)/(INDX(N)*(RADI(N+1)-RADI(N))+(INDX(N)-1)*THIC(N))  
			LHP=-1*RADI(N+1)*THIC(N)/(INDX(N)*(RADI(N+1)-RADI(N))+(INDX(N)-1)*THIC(N))              
		ENDIF

		PRINT LH,LHP,
		!Calculate focal length and print it
		P1=(CURV(N)-CURV(N+1))*(INDX(N)-1)
		P2=(INDX(N)-1)*(INDX(N)-1)*THIC(N)*CURV(N)*CURV(N+1)/INDX(N)
		F=1/(P1+P2)
		PRINT F,

		!Calculate l and l' and print it
		l=-(F-LH)
		lp=F+LHP
		PRINT l,lp,
		!Also print power of elements for convient
		PRINT (P1+P2)
	ENDIF
ENDIF
NEXT
