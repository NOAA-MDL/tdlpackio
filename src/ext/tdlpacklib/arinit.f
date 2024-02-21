      SUBROUTINE ARINIT(KFILDO,NOPEN,LSTRD,CFILE,KUSE,NIRW,MASTER,
     1                  NOPREC,KEYREC,CLIST,NFILSZ,KOUNT,
     2                  MAXOPN,MAXFIL,NW,NRAEND)
C 
C        NOVEMBER 1996   GLAHN   TDL   MOS-2000 
C        DECEMBER 2006   GLAHN   COMMENT CHANGE  
C        SEPTEMBER 2012   ENGLE      MDL   ADDED NRAEND TO THE CALL
C                         J. WAGNER        SEQUENCE.
C 
C        PURPOSE 
C            TO INITIALIZE COMMON BLOCK ARGC.  CALLED
C            FROM FLOPNM THE FIRST TIME IT IS CALLED.
C 
C        DATA SET USE. 
C            KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (OUTPUT) 
C 
C        VARIABLES 
C            INPUT 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE. 
C            NOPEN(N) = THE FORTRAN UNIT NUMBER CURRENTLY ASSOCIATED
C                       WITH AN OPEN FILE FOR EACH OF MAXOPN FILES
C                       (N=1,MAXOPN).  IF A FILE IS NOT OPEN FOR N,
C                       NOPEN(N) = 9999.
C          LSTRD(J,N) = THE RECORD NUMBER OF THE KEY RECORD LAST USED 
C                       (J=1) AND THE NUMBER OF THE ENTRY IN THE KEY
C                       RECORD LAST USED (J=2) FOR EACH OF THE MAXOPN
C                       FILES (N=1,MAXOPN).
C            CFILE(N) = THE FILE NAME ASSOCIATED WITH THE UNIT NUMBER
C                       IN NOPEN(N) FOR EACH OF MAXOPN FILES
C                       (N=1,MAXOPN).  (CHARACTER*1024)
C             KUSE(N) = RECORDS THE LAST USE OF EACH OF THE OPEN FILES
C                       BY STORING KOUNT WHENEVER FLOPNM IS ENTERED.
C                       (N=1,MAXOPN).
C             NIRW(N) = SET TO 1 WHEN FILE IS OPEN FOR READING ONLY AND
C                       SET TO 2 WHEN FILE IS OPEN FOR READING AND
C                       WRITING, FOR EACH OF OPEN FILES (N=1,MAXOPN).
C         MASTER(J,N) = 6 WORDS (J=1,6) OF THE MASTER KEY RECORD PLUS
C                       AN EXTRA WORD (J=7) INDICATING WHETHER (1) OR
C                       NOT (0) THIS MASTER KEY RECORD NEED BE WRITTEN
C                       WHEN CLOSING THE FILE FOR EACH OF THE MAXOPN 
C                       FILES (N=1,MAXOPN).  THE WORDS ARE: 
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
C         NOPREC(J,N) = 6 WORDS (J=1,6) USED BY THE FILE SYSTEM FOR EACH
C                       OF THE OPEN FILES (N=1,MAXOPN).  WORDS 3, 5,
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
C       KEYREC(J,L,N) = HOLDS THE KEY RECORDS FOR UP TO MAXOPEN OPEN
C                       FILES (N=1,MAXOPN), EACH KEY HAVING UP TO 
C                       NW ENTRIES (L=1,NW).  THE WORDS ARE:
C                       1-4 = THE 4 MOS-2000 IDS.
C                         5 = THE NUMBER OF DATA WORDS IN THE RECORD.
C                         6 =  THE BEGINNING RECORD NUMBER OF THE DATA 
C                              RECORD IN THE FILE * 1000 +
C                              THE NUMBER OF PHYSICAL RECORDS IN THE LOGICAL
C                              RECORD.
C            CLIST(J) = THE LIST OF FILE NAMES THAT HAVE BEEN OPENED 
C                       (J=1,MAXFIL).
C           CFILSZ(J) = THE PHYSICAL RECORD SIZE IN BYTES OF THE FILES
C                       APPEARING IN CLIST(J) (J=1,MAXFIL).  INITIALLY,
C                       ALL VALUES ARE ZERO.  WHEN A FILE IS OPENED, IT
C                       IS ENTERED IN CLIST( ) AND CFILSZ( ) FROM THE TOP.
C               KOUNT = THE TOTAL NUMBER OF TIMES FLOPNM HAS BEEN ENTERED.
C              MAXOPN = THE MAXIMUM NUMBER OF DIRECT ACCESS FILES THAT
C                       CAN BE OPEN IN THIS MOS-2000 EXTERNAL DIRECT
C                       ACCESS FILE SYSTEM.
C              MAXFIL = THE MAXIMUM NUMBER OF ENTRIES IN CLIST( ) AND
C                       CFILSZ( ).
C                  NW = THE MAXIMUM NUMBER OF ENTRIES IN ANY KEY RECORD
C                       BEING USED IN THIS RUN.
C           NRAEND(N) = HOLDS THE VALUE IRAEND (SET IN FLOPNM) FOR RA FILES THAT
C                       ARE OPEN, (N=1,MAXOPN).
C
C        NON SYSTEM SUBROUTINES USED
C            NONE
C
      CHARACTER*1024 CFILE,CLIST,BLANK
C
      DIMENSION NOPEN(MAXOPN),LSTRD(2,MAXOPN),CFILE(MAXOPN),
     1          KUSE(MAXOPN),NIRW(MAXOPN),MASTER(7,MAXOPN),
     2          NOPREC(6,MAXOPN),KEYREC(6,NW,MAXOPN),
     3          CLIST(MAXFIL),NFILSZ(MAXFIL),NRAEND(MAXOPN)
C
      DATA BLANK/' '/
C
      KOUNT=0
C
      DO 120 J=1,MAXOPN
      NOPEN(J)=9999
      LSTRD(1,J)=0
      LSTRD(2,J)=0
      KUSE(J)=0
      NIRW(J)=0
      CFILE(J)=BLANK(1:1024)
      NRAEND(J)=0
C
      DO 115 L=1,7
      MASTER(L,J)=0
 115  CONTINUE
C
      DO 117 M=1,NW
C
      DO 116 L=1,6
      KEYREC(L,M,J)=0
      NOPREC(L,J)=0
C
 116  CONTINUE
 117  CONTINUE
C
 120  CONTINUE
C
      DO 130 J=1,MAXFIL
      NFILSZ(J)=0
      CLIST(J)=BLANK
 130  CONTINUE
C
      RETURN
      END
