      SUBROUTINE PKMS00(KFILDO,IS1,ND7,IC,NXY,MINPK,INC,MISSP,MISSS,
     1                  JMAX,JMIN,LBIT,NOV,NDG,LX,IBIT,JBIT,KBIT,MINA)
C
C        FEBRUARY 1994   GLAHN   TDL   MOS-2000
C        JULY     1996   GLAHN   ADDED MISSS
C        MARCH    1997   GLAHN   /D DIAGNOSTICS ADDED
C        JUNE     1997   GLAHN   /D COMMENTED OUT, MAXA REMOVED
C 
C        PURPOSE 
C            CALLED BY PACK TO ASSIST IN PACKING DATA FOR MOS-2000.
C            IT IS USED WHEN THERE ARE NO MISSING VALUES IN THE DATA
C            THAT HAVE TO BE DEALT WITH.  THE SMALLEST VALUE IN IC( ) 
C            IS SUBTRACTED TO MAKE ALL VALUES POSITIVE.  SUBROUTINE
C            PACKGP IS CALLED.  DO NOT USE THIS ROUTINE WITH MISSP NE 0;
C            USE PKMS99 INSTEAD.
C
C        DATA SET USE 
C           KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE. (OUTPUT) 
C
C        VARIABLES 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (INPUT) 
C              IS1(L) = HOLDS THE VALUES FOR GRIB SECTION 1 
C                       (L=1,MAX OF ND7).  CARRIED FOR POSSIBLE PRINTING 
C                       OF IDENTIFICATION OF VARIABLE BEING DEALT WITH.
C                       (INPUT)
C                 ND7 = DIMENSION IF IS1( ).  (INPUT)
C               IC(K) = HOLDS VALUES TO PACK (K=NXY).  (INPUT)
C                 NXY = THE NUMBER OF VALUES IN IC( ).  ALSO USED AS
C                       THE DIMENSION OF IC( ).  (INPUT)
C               MINPK = VALUES ARE PACKED IN GROUPS OF MINIMUM SIZE
C                       MINPK.  ONLY WHEN THE NUMBER OF BITS TO HANDLE
C                       A GROUP CHANGES WILL A NEW GROUP BE FORMED.
C                       (INPUT)
C                 INC = THE NUMBER OF VALUES TO ADD AT A TIME TO A GROUP.
C                       (INPUT)
C               MISSP = WHEN MISSING POINTS CAN BE PRESENT IN THE DATA,
C                       THEY WILL HAVE THE VALUE MISSP OR MISSS.  MISSP
C                       IS THE PRIMARY MISSING VALUE AND IS USUALLY 9999,
C                       AND 9999 IS HARDCODED IN SOME SOFTWARE.  MISSS
C                       IS THE SECONDARY MISSING VALUE AND ACCOMMODATES
C                       THE 9997 PRODUCED BY SOME EQUATIONS FOR MOS
C                       FORECASTS.  MISSP = 0 INDICATES THAT NO MISSING
C                       VALUES (EITHER PRIMARY OR SECONDARY) ARE PRESENT.
C                       MISSS = 0 INDICATES THAT NO SECONDARY MISSING
C                       VALUES ARE PRESENT.  WHEN THIS ROUTINE IS ENTERED,
C                       MISSP AND MISSS SHOULD EQUAL ZERO.  IF THERE
C                       REALLY ARE MISSING VALUE INDICATORS IN THE DATA,
C                       THEY WILL BE TREATED JUST LIKE ALL OTHER VALUES;
C                       THESE INTEGER VALUE SHOULD BE PRESERVED.  (INPUT)
C               MISSS = SECONDARY MISSING VALUE INDICATOR (SEE MISSP).
C                       (INPUT)
C             JMAX(M) = THE MAXIMUM OF EACH GROUP M OF PACKED VALUES
C                       AFTER SUBTRACTING THE GROUP MINIMUM VALUE
C                       (M=1,LX).  (OUTPUT)
C             JMIN(M) = THE MINIMUM VALUE SUBTRACTED FOR EACH GROUP
C                       M (M=1,LX).  (OUTPUT)
C             LBIT(M) = THE NUMBER OF BITS NECESSARY TO HOLD THE
C                       PACKED VALUES FOR EACH GROUP M (M=1,LX). 
C                       (OUTPUT)
C              NOV(M) = THE NUMBER OF VALUES IN GROUP M (M=1,LX).
C                       (OUTPUT)
C                 NDG = DIMENSION OF JMAX( ), JMIN( ), LBIT( ), AND
C                       NOV( ).  (INPUT)
C                  LX = THE NUMBER OF GROUPS (THE NUMBER OF 2ND ORDER 
C                       MINIMA).  (OUTPUT)  
C                IBIT = THE NUMBER OF BITS NECESSARY TO PACK THE JMIN(J)
C                       VALUES, J=1,LX.  (OUTPUT)
C                JBIT = THE NUMBER OF BITS NECESSARY TO PACK THE LBIT(J),
C                       VALUES, J=1,LX.  (OUTPUT)
C                KBIT = THE NUMBER OF BITS NECESSARY TO PACK THE NOV(J),
C                       VALUES, J=1,LX.  (OUTPUT)
C                MINA = THE MINIMUM VALUE IN IC( ) BEFORE SUBTRACTING 
C                       THE MINIMUM VALUE.  (OUTPUT)
C
C        NON SYSTEM SUBROUTINES CALLED 
C           PACKGP
C
      DIMENSION IS1(ND7)
      DIMENSION IC(NXY)
      DIMENSION JMAX(NDG),JMIN(NDG),NOV(NDG),LBIT(NDG)
C
C
C        FIND THE MAX AND MIN VALUES.
C
 105  MINA=IC(1)
C
      DO 125 K=2,NXY
      IF(IC(K).LT.MINA)MINA=IC(K)
 125  CONTINUE
C
C***D     WRITE(KFILDO,126)(IC(J),J=1,400)
C***D126  FORMAT(/' IC( ) IN PKMS00'/(' '20I5))
C
      DO 130 K=1,NXY
      IC(K)=IC(K)-MINA
 130  CONTINUE
C
C***D     WRITE(KFILDO,131)MINA
C***D131  FORMAT(/' MINA IN PKMS00 ='I6)
C***D     WRITE(KFILDO,126)(IC(J),J=1,400)
C
C        CALL PACKGP TO CALCULATE LX, JMIN( ), JMAX( ), LBIT( ),
C        AND NOV( ).
C
      CALL PACKGP(KFILDO,IC,NXY,MINPK,INC,MISSP,MISSS,
     1           JMIN,JMAX,LBIT,NOV,NDG,LX,IBIT,JBIT,KBIT)
C
C        SUBTRACT LOCAL MIN FOR EACH OF LX GROUPS.
C
      K=0
C
      DO 153 L=1,LX
      DO 152 M=1,NOV(L)
      K=K+1
      IC(K)=IC(K)-JMIN(L)
 152  CONTINUE
 153  CONTINUE
C
      RETURN
      END
