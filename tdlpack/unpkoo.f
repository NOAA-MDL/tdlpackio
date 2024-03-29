      SUBROUTINE UNPKOO(KFILDO,IPACK,ND5,LOC,IPOS,
     1                  MINA,JMIN,LBIT,NOV,LX,IWORK,L3264B,IER)
C
C        JUNE  1997   GLAHN   TDL   MOS-2000
C        APRIL 2000   DALLAVALLE   MODIFIED FORMAT STATEMENTS TO
C                                  CONFORM TO FORTRAN 90 STANDARDS
C                                  ON THE IBM SP
C
C        PURPOSE 
C            UNPACKS DATA IN TDLPACK FORMAT WHEN THERE ARE NO
C            MISSING VALUES.  SCALING IS NOT DONE IN THIS ROUTINE,
C            BUT THE REFERENCE VALUE IS USED.  CALLED FROM UNPACK
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
C                       LE 32.  UPDATED AS NECESSARY
C                       AFTER PACKING IS COMPLETED.  (INPUT-OUTPUT)
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
C                       7 = IPOS NOT IN RANGE 1 TO 32.
C                       8 = LBIT(L) NOT IN RANGE 0 TO 30.
C        NON SYSTEM SUBROUTINES CALLED
C            NONE
C
      DIMENSION IPACK(ND5),IWORK(ND5)
      DIMENSION JMIN(LX),LBIT(LX),NOV(LX)
C
C        CHECK CORRECTNESS OF INPUT AND SET STATUS RETURN.
C
      IER=0
C
      IF(IPOS.LE.0.OR.IPOS.GT.L3264B)THEN
         IER=7
         WRITE(KFILDO,101)IPOS,IER
 101     FORMAT(/,' IPOS = ',I6,' NOT IN THE RANGE 1 TO L3264B.',
     1            '  RETURN FROM UNPKOO WITH IER = ',I4)
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
     1           ' NOT IN THE RANGE',
     2           ' 0 TO 30.  RETURN FROM UNPKOO WITH IER = ',I4)
         GO TO 900
      ENDIF
C
      IF(LBIT(L)*NOV(L).GT.(L3264B+1-IPOS)+(ND5-LOC)*L3264B)THEN
         IER=6
         WRITE(KFILDO,103)NOV(L),LBIT(L),L,LOC,IPOS,ND5,IER
 103     FORMAT(/,' ****NOV(L) = ',I9,' AND LBIT(L) = ',I6,' FOR L =',
     1          I6,
     2          ' REQUIRE MORE BITS THAN ARE AVAILABLE IN IPACK( ),',/,
     3          '     WITH LOC =',I8,', IPOS =',I4,', AND ND5 =',I8,
     4          '.','  RETURN FROM UNPKOO WITH IER =',I4)
         GO TO 900
      ENDIF
C
      IF(NOV(L)+K.GT.ND5)THEN
         IER=6
         WRITE(KFILDO,104)NOV(L),L,ND5,IER
 104     FORMAT(/,' ****NOV(L) = ',I9,' FOR L =',I6,
     1          ' INDICATES MORE VALUES THAN CAN BE PUT INTO IWORK( ),'
     2          ,/,'     WITH ND5 =',I8,'.',
     3          '  RETURN FROM UNPKOO WITH IER =',I4)
         GO TO 900
      ENDIF
C
      JMINLA=JMIN(L)+MINA
C        THE ABOVE DEFINITION MAY IMPROVE EFFICIENCY.
C
C        TEST FOR LBIT(L) = 0 OUT OF LOOP.
C
      IF(LBIT(L).NE.0)GO TO 330
C
      DO 249 M=1,NOV(L)
      IWORK(K+M)=JMINLA
 249  CONTINUE
C
      K=K+NOV(L)
      GO TO 350
C
 330  DO 349 M=1,NOV(L)
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
 340  IWORK(K+M)=JMINLA+NVALUE
 349  CONTINUE
C
      K=K+NOV(L)
 350  CONTINUE
C
 900  RETURN
      END
