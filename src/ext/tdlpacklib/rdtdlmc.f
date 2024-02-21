      SUBROUTINE RDTDLMC(KFILDO,KFILX,CFILX,ID,RECORD,NSIZE,NVALUE,
     1                   L3264B,IER) 
C 
C        SEPTEMBER 2012  ENGLE   MDL MOS-2000, ADAPTED FROM RDTDLM
C 
C        PURPOSE 
C            TO READ A STATION CALL LETTER RECORD TO FROM MOS-2000
C            EXTERNAL DIRECT ACCESS SYSTEM.  THIS INCLUDES OPENING
C            THE FILE, READING THE MASTER KEY RECORD WHEN NECESSARY,
C            AND MAKING A KEY RECORD AVAILABLE IN MASTER( , ).
C 
C        DATA SET USE. 
C            KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (OUTPUT) 
C            KFILX  - UNIT NUMBER FOR TDL FILE.  (INPUT) 
C 
C        VARIABLES 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (INPUT) 
C               KFILX = UNIT NUMBER FOR TDL FILE.  (INPUT) 
C               CFILE = THE NAME OF THE FILE TO OPEN.  (CHARACTER*1024)
C                       (INPUT)
C               ID(J) = THE 4 MOS IDS OF THE RECORD TO READ (J=1,4).
C                       (INPUT)
C           RECORD(J) = THE CHARACTER(LEN=L3264B/8) ARRAY TO STATION
C                       CALL LETTERS DATA INTO (J=1,NSIZE).  (OUTPUT)
C               NSIZE = THE SIZE OF RECORD( ).  (OUTPUT)
C              NVALUE = THE NUMBER OF DATA VALUES READ INTO RECORD( ).
C                       (OUTPUT)
C              L3264B = 32 FOR A 32-BIT WORKSTATION;
C                       64 FOR THE 64-BIT CRAY.  (INPUT)
C                 IER = STATUS CODE.
C                       0 = GOOD RETURN.
C                       OTHER VALUES FROM CALLED ROUTINES.
C                       (OUTPUT)
C
C         COMMON BLOCK       
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
C                       6 = THE RECORD NUMBER OF THE NEXT KEY RECORD
C                           IN THE FILE.  EQUALS 9999 WHEN THIS IS THE
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
C                       ACCESS FILE SYSTEM.  (SET BY PARAMETER)
C              MAXFIL = THE MAXIMUM NUMBER OF ENTRIES IN CLIST( ) AND
C                       CFILSZ( ).  (SET BY PARAMETER)
C                  NW = THE MAXIMUM NUMBER OF ENTRIES IN ANY KEY RECORD
C                       BEING USED IN THIS RUN. 840 WILL ACCOMMODATE A
C                       20,000 BYTE RECORD.  (SET BY PARAMETER)
C              IRAEND = INTEGER VALUE THAT REPRESENTS THE ENDIAN OF
C                       A RANDOM ACCESS FILE.
C                        -1 = LITTLE-ENDIAN
C                         1 = BIG-ENDIAN
C             ISYSEND = HOLD THE VALUE THAT REPRESENTS THE SYSTEM
C                       ENDIAN. (INPUT/OUTPUT)
C                       THIS IS SET BY CALLING CKSYSEND
C                        -1 = SYSTEM IS LITLE-ENDIAN.
C                         1 = SYSTEM IS BIG-ENDIAN.
C
C        NON SYSTEM SUBROUTINES USED 
C            FLOPNM, RDTM, CKSYSEND 
C 
      PARAMETER (MAXOPN=2,
     1           MAXFIL=20, 
     2           NW=840) 
C
      CHARACTER(LEN=L3264B/8), DIMENSION(NSIZE) :: RECORD
      CHARACTER*1024 CFILX,CFILE,CLIST
C
      COMMON/ARGC/NOPEN(MAXOPN),LSTRD(2,MAXOPN),CFILE(MAXOPN),
     1            KUSE(MAXOPN),NIRW(MAXOPN),MASTER(7,MAXOPN),
     2            NOPREC(6,MAXOPN),KEYREC(6,NW,MAXOPN),
     3            CLIST(MAXFIL),NFILSZ(MAXFIL),KOUNT,
     4            NRAEND(MAXOPN)
C
      DIMENSION ID(4)
C     DIMENSION RECORD(NSIZE)
C
      IER=0
      IRW=1
C        READING IS TO BE DONE.
C
      CALL FLOPNM(KFILDO,KFILX,CFILX,IRW,NT,L3264B,IRAEND,IER)
      IF(IER.NE.0)GO TO 200
C
      CALL RDTMC(KFILDO,KFILX,ID,RECORD,NSIZE,NVALUE,
     1          KEYREC(1,1,NT),LSTRD(1,NT),
     2          NOPREC(1,NT),MASTER(1,NT),NW,L3264B,IER) 
C     
 200  RETURN
      END
