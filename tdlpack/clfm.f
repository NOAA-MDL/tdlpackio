      SUBROUTINE CLFM(KFILDO,KFILX,CFILE,NOPEN,NOPREC,MASTER,
     1                LSTRD,KEYREC,NW,IER) 
C 
C        NOVEMBER 1996   GLAHN      TDL   MOS-2000
C        MARCH    2000   DALLAVALLE MODIFIED FORMAT STATEMENTS TO
C                                   CONFORM TO FORTRAN 90 STANDARDS
C                                   ON IBM SP
C        DECEMBER 2006   GLAHN      COMMENT CHANGE  
C
C        PURPOSE 
C            TO CLOSE A MOS-2000 EXTERNAL DIRECT ACCESS FILE.
C            THE KEY AND MASTER KEY RECORDS ARE WRITTEN AS NECESSARY. 
C 
C        DATA SET USE 
C            KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (OUTPUT) 
C            KFILX  - UNIT NUMBER FOR THE MOS-2000 FILE TO CLOSE.  (OUTPUT) 
C 
C        VARIABLES 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (INPUT)
C               KFILX = FORTRAN UNIT OF FILE TO CLOSE.  (INPUT)
C               CFILE = THE NAME OF THE FILE ASSOCIATED WITH UNIT KFILX.
C                       (CHARACTER*1024)  (INPUT-OUTPUT) 
C               NOPEN = THE FORTRAN UNIT NUMBER CURRENTLY ASSOCIATED WITH 
C                       THE OPEN FILE.  WHEN THE FILE IS CLOSED, 
C                       NOPEN IS SET = 9999.  (INPUT-OUTPUT)
C           NOPREC(J) = 6 WORDS (J=1,6) USED BY THE FILE SYSTEM.  WORDS 3, 5,
C                       AND 6 ARE WRITTEN AS PART OF THE KEY RECORD.
C                       THE WORDS ARE:
C                       1 = IS THE KEY RECORD IN KEYREC( , , )?  IF NOT,
C                           THIS VALUE IS ZERO.  OTHERWISE, LOCATION 
C                           IN KEYREC( , ,N) OF THE KEY RECORD, RANGE OF
C                           1 TO MAXOPN.
C                       2 = LOCATION OF THIS KEY RECORD IN THE FILE.
C                       3 = NUMBER OF SLOTS FILLED IN THIS KEY.
C                       4 = INDICATES WHETHER (1) OR NOT (0) THE KEY
C                           RECORD HAS BEEN MODIFIED AND NEEDS TO BE
C                           WRITTEN.  ZERO INITIALLY.
C                       5 = NUMBER OF PHYSICAL RECORDS IT TAKES TO HOLD
C                           THIS LOGICAL KEY RECORD.  THIS IS FILLED BY
C                           WRKEYM.
C                       6 = THE RECORD NUMBER OF THE NEXT KEY RECORD IN
C                           THE FILE.  EQUALS 99999999 WHEN THIS IS THE
C                           LAST KEY RECORD IN THE FILE.
C                       (INPUT-OUTPUT)
C           MASTER(J) = 6 WORDS (J=1,6) OF THE MASTER KEY RECORD PLUS
C                       AN EXTRA WORD (J=7) INDICATING WHETHER (1) OR
C                       NOT (0) THIS MASTER KEY RECORD NEED BE WRITTEN
C                       WHEN CLOSING THE FILE .  THE WORDS ARE: 
C                       1 = RESERVED.  SET TO ZERO.
C                       2 = NUMBER OF INTEGER WORDS IN ID FOR EACH
C                           RECORD.  THIS IS 4 UNLESS CHANGES ARE
C                           MADE TO THE SOFTWARE.
C                       3 = THE NUMBER OF WORDS IN A PHYSICAL RECORD.
C                           THIS APPLIES TO A 32-BIT OR A 64-BIN 
C                           MACHINE.
C                       4 = NUMBER OF KEY RECORDS STORED IN THE FILE
C                           TO WHICH THIS MASTER KEY REFERS.
C                           INITIALLY = 1.
C                       5 = MAXIMUM NUMBER OF KEYS IN A KEY RECORD 
C                           FOR THIS FILE.
C                       6 = LOCATION OF WHERE THE FIRST PHYSICAL RECORD
C                           OF THE LAST LOGICAL KEY RECORD OF THE FILE
C                           IS LOCATED.
C                       7 = THIS MASTER KEY RECORD HAS (1) HAS NOT (0)
C                           BEEN MODIFIED.
C                       (INPUT-OUTPUT)
C            LSTRD(J) = THE RECORD NUMBER OF THE KEY RECORD LAST USED 
C                       (J=1) AND THE NUMBER OF THE ENTRY IN THE KEY
C                       RECORD LAST USED (J=2).
C                       (INPUT-OUTPUT)
C         KEYREC(J,L) = HOLDS THE KEY RECORD OF THE OPEN FILE, EACH KEY
C                       HAVING UP TO NW ENTRIES (L=1,NW).  THE WORDS ARE:
C                       1-4 = THE 4 MOS-2000 IDS.
C                         5 = THE NUMBER OF DATA WORDS IN THE RECORD.
C                         6 =  THE BEGINNING RECORD NUMBER OF THE DATA 
C                              RECORD IN THE FILE * 1000 +
C                              THE NUMBER OF PHYSICAL RECORDS IN THE LOGICAL
C                              RECORD.
C                       (INPUT)
C                  NW = SECOND DIMENSION OF KEYREC( , ).  (INPUT)
C                 IER = STATUS RETURN
C                       0 = GOOD RETURN.
C                       OTHER RETURNS FROM SYSTEM OR CALLED ROUTINES.
C                       (OUTPUT)
C 
C        NONSYSTEM SUBROUTINES CALLED 
C            WRKEYM, TDLPRM (/D ONLY) 
C 
      CHARACTER*4 STATE
      CHARACTER*1024 CFILE,
     1             BLANK/' '/
C
      DIMENSION KEYREC(6,NW),LSTRD(2),NOPREC(6),MASTER(7) 
C
      IER=0
C 
CD     CALL TDLPRM(KFILDO,'CLFM BEG') 
C 
      IF(NOPREC(4).EQ.0)GO TO 140 
C        THE KEY RECORD MUST BE WRITTEN. 
      CALL WRKEYM(KFILDO,KFILX,NOPREC,KEYREC,MASTER(5)*6,
     1            MASTER(3),'CLFM  ',IER)
      IF(IER.NE.0)GO TO 902 
C
 140  IF(MASTER(7).EQ.0)GO TO 145 
C       THE MASTER KEY RECORD MUST BE WRITTEN. 
      MASTER(6)=MAX(MASTER(6),NOPREC(2))
C        MASTER(6) IS THE RECORD NUMBER OF THE LAST KEY IN THE FILE.
      STATE=' 140' 
      WRITE(KFILX,REC=1,IOSTAT=IOS,ERR=900)(MASTER(J),J=1,6) 
C        NOTE THAT ONLY 6 WORDS OF MASTER( ) ARE WRITTEN.
C
C        SET VALUES IN NOPEN, CFILM, LSTRD( ), MASTER( ), AND 
C        NOPREC( ) TO INDICATE FILE IS CLOSED.
C 
 145  CLOSE(NOPEN)
      NOPEN=9999 
      LSTRD(1)=0 
      LSTRD(2)=0 
      CFILE=BLANK 
C
      DO 146 J=1,6
      MASTER(J)=0
      NOPREC(J)=0
 146  CONTINUE
C
      MASTER(7)=0
C
CD     CALL TDLPRM(KFILDO,'CLFM END') 
      GO TO 902 
C 
C        THIS SECTION FOR SYSTEM ERROR DIAGNOSTICS. 
C 
 900  WRITE(KFILDO,901)KFILX,STATE,IOS
 901  FORMAT(/,' ****ERROR WRITING MASTER KEY RECORD IN CLFM',
     1         ' ON UNIT NO.',I3,' AT ',A4,'  IOSTAT =',I5)
      IER=IOS
C
 902  RETURN 
      END 
