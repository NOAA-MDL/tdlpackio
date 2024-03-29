      SUBROUTINE UNPKPS(KFILDO,IPACK,ND5,LOC,IPOS,MISSP,MISSS,
     1                  MINA,JMIN,LBIT,NOV,LX,IWORK,L3264B,IER)
C
C        JUNE 1997   GLAHN   TDL   MOS-2000
C        APRIL 2000   DALLAVALLE   MODIFIED FORMAT STATEMENTS TO
C                                  CONFORM TO FORTRAN 90 STANDARDS
C                                  ON THE IBM SP
C        NOVEMBER 2002        SU   CHANGED 'UNPKOO' TO 'UNPKPS' IN FORMAT NO. 104.
C
C        PURPOSE 
C            UNPACKS DATA IN TDLPACK FORMAT WHEN THERE CAN BE PRIMARY
C            AND SECONDARY MISSING VALUES.  SCALING IS NOT DONE IN THIS
C            ROUTINE, BUT THE REFERENCE VALUE IS USED.  CALLED FROM UNPACK
C            TO ELIMINATE MULTIPLE CALLS TO UNPKBG.  THE WORD
C            POINTER LOC AND BIT POSITION POINTER IPOS ARE UPDATED
C            AS NECESSARY.
C
C        DATA SET USE 
C           KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE. (OUTPUT) 
C
C        VARIABLES 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (INPUT)
C            IPACK(J) = ARRAY TO UNPACK FROM (J=1,ND5).  (INPUT)
C                 ND5 = DIMENSION OF IPACK( ).  (INPUT)
C                 LOC = WORD IN IPACK( ) TO START UNPACKING.  UPDATED
C                       AS NECESSARY AFTER UNPACKING IS COMPLETED.
C                       (INPUT-OUTPUT)
C                IPOS = BIT POSITION (COUNTING LEFTMOST BIT IN WORD
C                       AS 1) TO START UNPACKING.  MUST BE GE 1 AND
C                       LE L3264B.  UPDATED AS NECESSARY
C                       AFTER PACKING IS COMPLETED.  (INPUT-OUTPUT)
C               MISSP = THE PRIMARY MISSING VALUE TO RETURN IN IWORK( )
C                       WHEN THE PACKED DATUM INDICATES A PRIMARY
C                       MISSING VALUE.  (INPUT)
C               MISSS = THE SECONDARY MISSING VALUE TO RETURN IN IWORK( )
C                       WHEN THE PACKED DATUM INDICATES A SECONDARY
C                       MISSING VALUE.  (INPUT)
C                MINA = THE REFERENCE VALUE.  (INPUT)
C             JMIN(L) = THE MINIMUM VALUE SUBTRACTED FROM EACH GROUP
C                       L BEFORE PACKING (L=1,LX).  (INPUT)
C             LBIT(L) = THE NUMBER OF BITS NECESSARY TO HOLD THE
C                       PACKED VALUES FOR EACH GROUP L (L=1,LX). 
C                       (INPUT)
C              NOV(L) = THE NUMBER OF VALUES IN GROUP L (L=1,LX).
C                       (INPUT)
C                  LX = THE NUMBER OF VALUES IN LBIT( ), JMIN( ), AND
C                       NOV( ).  ALSO USED AS THEIR DIMENSIONS.  (INPUT)
C            IWORK(J) = THE UNPACKED DATA ARE RETURNED (J=1,MAX OF ND5).
C                       THE NUMBER OF VALUES IS NXY IN SOME ROUTINES
C                       BUT IS DETERMINED HERE BY THE LX VALUES IN
C                       NOV( ).  (OUTPUT)
C              L3264B = INTEGER WORD LENGTH OF MACHINE BEING USED.
C                       (INPUT)
C                 IER = STATUS RETURN:
C                       0 = GOOD RETURN.
C                       6 = NOT ENOUGH ROOM IN IPACK( ) OR IWORK( ) TO
C                           ACCOMMODATE THE DATA INDICATED BY LBIT( )
C                           AND NOV( ).
C                       7 = IPOS NOT IN RANGE 1 TO L3264B.
C                       8 = LBIT(L) NOT IN RANGE 0 TO 30.
C        NON SYSTEM SUBROUTINES CALLED
C            NONE
C
      DIMENSION IPACK(ND5),IWORK(ND5)
      DIMENSION JMIN(LX),LBIT(LX),NOV(LX)
C
      DIMENSION LB2M1(0:30),LB2M2(0:30)
C
      SAVE LB2M1,LB2M2
C
      DATA IFIRST/0/
C
C         CALCULATE THE POWERS OF 2 THE FIRST TIME ENTERED.
C
      IF(IFIRST.EQ.0)THEN
         IFIRST=1
         LB2M1(0)=0
         LB2M2(0)=-1
C
         DO 100 J=1,30
         LB2M1(J)=(LB2M1(J-1)+1)*2-1
         LB2M2(J)=(LB2M2(J-1)+2)*2-2
 100     CONTINUE
C
      ENDIF
C
C        CHECK CORRECTNESS OF INPUT AND SET STATUS RETURN.
C
      IER=0
C
      IF(IPOS.LE.0.OR.IPOS.GT.L3264B)THEN
         IER=7
         WRITE(KFILDO,101)IPOS,IER
 101     FORMAT(/,' IPOS = ',I6,' NOT IN THE RANGE 1 TO L3264B.',
     1            '  RETURN FROM UNPKPS WITH IER = ',I4)
         GO TO 900 
      ENDIF
C
      K=0
C
      DO 350 L=1,LX
      IF(LBIT(L).LT.0.OR.LBIT(L).GT.30)THEN
         IER=8
         WRITE(KFILDO,102)LBIT(L),L,IER
 102     FORMAT(/,' ****LBIT(L) = ',I6,' FOR L =',I6,
     1            ' NOT IN THE RANGE 0 to 30. ',
     2            ' RETURN FROM UNPKPS WITH IER = ',I4)
         GO TO 900
      ENDIF
C
      IF(LBIT(L)*NOV(L).GT.(L3264B+1-IPOS)+(ND5-LOC)*L3264B)THEN
         IER=6
         WRITE(KFILDO,103)NOV(L),LBIT(L),L,LOC,IPOS,ND5,IER
 103     FORMAT(/,' ****NOV(L) = ',I9,' AND LBIT(L) = ',I6,
     1            ' FOR L =',I6,' REQUIRE MORE BITS THAN',
     2            ' ARE AVAILABLE IN IPACK( ),',/,'     WITH',
     3            ' LOC =',I8,', IPOS =',I4,', AND ND5 =',I8,'.',
     4            '  RETURN FROM UNPKPS WITH IER =',I4)
         GO TO 900
      ENDIF
C
      IF(NOV(L)+K.GT.ND5)THEN
         IER=6
         WRITE(KFILDO,104)NOV(L),L,ND5,IER
 104     FORMAT(/,' ****NOV(L) = ',I9,' FOR L =',I6,' INDICATES MORE',
     1            ' VALUES THAN CAN BE PUT INTO IWORK( ),',/,
     2            '     WITH ND5 =',I8,'.',
     3            '  RETURN FROM UNPKPS WITH IER =',I4)
         GO TO 900
      ENDIF
C
      JMINLA=JMIN(L)+MINA
      MISSPK=LB2M1(LBIT(L))
      MISSSK=LB2M2(LBIT(L))
C        THE ABOVE DEFINITIONS MAY IMPROVE EFFICIENCY.
C
C        NOTE THAT IT IS NOT NECESSARY TO TEST FOR LBIT(L) EQ 0,
C        AS IT IS IN UNPKOO AND UNPKPO, BECAUSE THIS CANNOT BE
C        TRUE WHEN THERE CAN BE SECONDARY MISSING VALUES.
C
      DO 349 M=1,NOV(L)
      K=K+1
C
C        SHIFT WORD IPACK(LOC) TO LEFT TO ELIMINATE BITS TO LEFT OF THOSE
C        WANTED, THEN BACK TO THE RIGHT TO THE PORTION OF THE WORD
C        WANTED.
C
      NVALUE=ISHFT(ISHFT(IPACK(LOC),IPOS-1),LBIT(L)-L3264B)
C
C        UPDATE IPOS AND LOC AS NEEDED.
C
      IPOS=IPOS+LBIT(L)
      IF(IPOS.LE.L3264B)GO TO 340
      LOC=LOC+1
      IPOS=IPOS-L3264B
      IF(IPOS.EQ.1)GO TO 340
C   
C        FINISH UNPACKING.
C
      NVALUE=IOR(NVALUE,ISHFT(IPACK(LOC),IPOS-(L3264B+1))) 
C
 340  IF(NVALUE.EQ.MISSPK)THEN
         IWORK(K)=MISSP
      ELSEIF(NVALUE.EQ.MISSSK)THEN
         IWORK(K)=MISSS
      ELSE
         IWORK(K)=JMINLA+NVALUE
C
         IF(IWORK(K).EQ.MISSP)THEN
            IWORK(K)=IWORK(K)-1
         ELSEIF(IWORK(K).EQ.MISSS)THEN
            IWORK(K)=IWORK(K)-1
         ENDIF
C           THE ABOVE STATEMENTS ARE NECESSARY TO GUARD AGAINST A 
C           LEGITIMATE VALUE BEING INTERPRETED AS A MISSING.
C           SINCE MISSP IS SCALED * 10000, THIS SHOULD BE
C           EXTREMELY RARE.  MISSS MUST NOT BE EXACTLY ONE 
C           LESS THAN MISSP.
C
      ENDIF
C
 349  CONTINUE
C
 350  CONTINUE
C
 900  RETURN
      END
