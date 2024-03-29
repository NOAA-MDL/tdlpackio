      SUBROUTINE MCLLIJ(KFILDO,ALAT,ALON,XMESHL,XLAT,
     1                  XLATLL,XLONLL,XI,YJ)
C
C        MAY      2002   GLAHN   TDL   MOS-2000
C        JULY     2002   GLAHN   ADDED DIAGNOSTIC PRINT 100
C
C        PURPOSE
C            TO CONVERT FROM LATITUDE, LONGITUDE TO GRID COORDINATES ON
C            A MERCATOR PROJECTION WITH THE LATITUDE OF SECANCY
C            IN THE NORTHERN HEMISPHERE.  ADAPTED FROM NMC'S W3FB08,
C            WITH THE INPUT CHANGED FROM EAST TO WEST LONGITUDE.
C            ALTHOUGH THE INPUT IS IN W LONGITUDE, THE COMPUTATIONS,
C            BEING BASED ON THOSE IN W3FB08, ARE IN TERMS OF EAST
C            LONGITUDE.  FORMULAE AND NOTATION LOOSELY BASED ON HOKE,
C            HAYES, AND RENNINGER'S "MAP PROJECTIONS AND GRID 
C            SYSTEMS...", MARCH 1981, AFGWC/TN-79/003.  ORIGINAL AUTHOR,
C            STACKPOLE.
C
C        DATA SET USE
C            KFILDO - UNIT NUMBER OF OUTPUT (PRINT) FILE.  (OUTPUT)
C
C        VARIABLES
C            INPUT
C              KFILDO = UNIT NUMBER OF OUTPUT (PRINT) FILE.  (INPUT)
C                ALAT = NORTH LATITUDE IN DEGREES FOR WHICH THE GRID
C                       COORDINATES ARE WANTED.  NEGATIVE FOR 
C                       SOUTHERN HEMSIPHERE.
C                ALON = WEST LONGITUDE IN DEGREES FOR WHICH THE GRID
C                       COORDINATES ARE WANTED.  DO NOT USE NEGATIVE. 
C              XMESHL = MESH LENGTH IN METERS AT XLAT DEGREES N
C                       LATITUDE.
C                XLAT = LATITUDE IN DEGREES AT WHICH XMESHL APPLIES. 
C                       ALSO THE LATITUDE WHERE THE PROJECTION CUTS THE 
C                       EARTH.  DO NOT USE NEGATIVE.
C              XLATLL = LATITUDE OF LOWER LEFT (1,1) CORNER POINT OF THE
C                       GRID.
C              XLONLL = WEST LONGITUDE OF LOWER LEFT (1,1) CORNER POINT
C                       OF THE GRID.  DO NOT USE NEGATIVE.
C
C            OUTPUT
C               XI,YJ = IJ (LEFT TO RIGHT) AND JY (BOTTON TO TOP)
C                       GRIDPOINT NUMBERS OF THE POINT ALAT, ALON,
C                       CONSIDERING THE LOWER LEFT CORNER POINT TO
C                       BE (1,1).
C
C            INTERNAL
C              RADPDG = NUMBER OF RADIANS PER DEGREE.  SET BY PARAMETER.
C                  PI = PI.  SET BY PARAMETER.
C               RERTH = RADIUS OF THE EARTH IN METERS.  SET BY
C                       PARAMETER.
C              DEGPRA = DEGREES PER RADIAN.  SET BY PARAMETER.
C        1         2         3         4         5         6         7 X
C
C        NONSYSTEM ROUTINES CALLED
C            NONE 
C
      PARAMETER (PI=3.14159,
     1           RERTH=6371200.,
     2           RADPDG=PI/180.,
     3           DEGPRA=180./PI)
C
      IF(XMESHL.LE.0..OR.XLAT.LT.0..OR.XLONLL.LT.0.)THEN
         WRITE(KFILDO,100)XMESHL,XLAT,XLONLL
 100     FORMAT(/' ****PROBLEM WITH EITHER'/
     1           '     XMESHL =',F12.4,','/
     2           '     XLAT   =',F12.4,', OR'/
     3           '     XLONLL =',F12.4,'.'/
     4           '     STOP IN MCLLIJ AT 100.')
         STOP 100
      ENDIF
C
C        PRELIMINARY VARIABLES AND REDIFINITIONS
C
      CLAIN = COS(RADPDG*XLAT)
      DELLON = XMESHL/(RERTH*CLAIN)
C
C        GET DISTANCE FROM EQUATOR TO ORIGIN XLATLL
C
      DJEO = 0.
      IF(XLATLL.NE.0.)
     1  DJEO = (ALOG(TAN(0.5*((XLATLL+90.0)*RADPDG))))/DELLON
C
C        NOW THE I AND J COORDINATES
C
      XI = 1. - ((ALON - XLONLL)/(DELLON*DEGPRA))
C        SIGN CHNAGED FROM + TO - BEFORE THE PARENTHESES TO ACCOUNT
C        FOR INPUT BEING IN W RATHER THAN E LONGITUDE.
      YJ = 1. + (ALOG(TAN(0.5*((ALAT + 90.) * RADPDG))))/
     1            DELLON - DJEO
C
D     WRITE(KFILDO,900)ALAT,ALON,XMESHL,XLAT,XLATLL,XLONLL,XI,YJ
D900  FORMAT(' IN MCLLIJ--ALAT,ALON,XMESHL,XLAT,XLATLL,XLONLL,XI,YJ',
D    1         9F10.2)
C
      RETURN
      END
