      SUBROUTINE WRDATM(KFILDO,KFILX,JREC,RECORD,NSIZE,KSIZE,CFROM,IER)
C 
C        NOVEMBER  1996   GLAHN      TDL   MOS-2000
C        APRIL     2000   DALLAVALLE MODIFIED FORMAT STATEMENTS TO
C                                    CONFORM TO FORTRAN 90 STANDARDS
C                                    ON THE IBM SP
C        DECEMBER  2006   GLAHN      INSERTED CHECK ON NUMBER OF PHYSICAL
C                                    RECORDS EXCEEDING 999 AT 150; ERROR
C                                    CODE IER = 150
C        
C        PURPOSE 
C            TO WRITE A LOGICAL DATA RECORD TO THE EXTERNAL MOS-2000
C            DIRECT ACCESS FILE SYSTEM.  THE LOGICAL RECORD CAN SPAN 
C            MORE THAN ONE PHYSICAL RECORD.  CALLED BY FLOPNM, WRTDLM. 
C 
C        DATA SET USE 
C            KFILDO - UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (OUTPUT) 
C            KFILX  - UNIT NUMBER FOR MOS-2000 FILE.  (OUTPUT) 
C 
C        VARIABLES 
C 
C              KFILDO = UNIT NUMBER FOR OUTPUT (PRINT) FILE.  (INPUT) 
C               KFILX = UNIT NUMBER FOR MOS-2000 FILE.  (INPUT) 
C                JREC = RECORD NUMBER * 1000 OF 1ST PHYSICAL RECORD
C                       TO WRITE TO FILE NUMBER KFILX.  IT IS UPDATED
C                       TO INDICATE THE NUMBER OF PHYSICAL RECORDS IN
C                       THE LOGICAL RECORD.  (INPUT-OUTPUT)
C           RECORD(J) = DATA TO WRITE TO LOGICAL RECORD (J=1,NSIZE).
C                       (INPUT) 
C               NSIZE = NO. OF DATA WORDS TO WRITE.  SEE RECORD( ).
C                       (INPUT) 
C               KSIZE = SIZE OF PHYSICAL RECORD.  (INPUT)
C               CFROM = 6 CHARACTERS TO IDENTIFY CALLING PROGRAM.
C                       (CHARACTER*6)  (INPUT)
C                 IER = STATUS RETURN.
C                         0 = GOOD RETURN.
C                       150 = NUMBER OF PHYSICAL RECORDS IN THE
C                             LOGICAL RECORD EXCEEDS 999.
C                       152 = RECORD NUMBER OF PHYSICAL RECORD SIZE
C                             INCORRECT.
C                       OTHER VALUES FROM SYSTEM.
C                       (OUTPUT)
C 
C        NONSYSTEM SUBROUTINES CALLED 
C            NONE 
C 
      CHARACTER*6 CFROM
C
      DIMENSION RECORD(NSIZE)
C 
      IER=0
C
      MREC=JREC/1000
C
      IF(MREC.LE.0.OR.
     1   KSIZE.LE.0)THEN
         WRITE(KFILDO,110)MREC,KSIZE,KFILX,CFROM
 110     FORMAT(/,' ****EITHER THE RECORD NUMBER = ',I4,
     1            ' OR THE PHYSICAL RECORD SIZE =',I7,
     2            ' IS IN ERROR IN WRDATM FOR UNIT NO.',I3,'.',/,
     3            '     WRDATM CALLED FROM ',A6)
         IER=152
         GO TO 902
C
      ENDIF
C
      K=0
      NSTART=1
C        NSTART IS THE FIRST WORD TO WRITE FROM RECORD( ).
      NREMIN=NSIZE
C        NREMIN IS THE NUMBER OF WORDS REMAINING TO WRITE.
 120  NEND=NSTART-1+MIN(KSIZE,NREMIN)
      WRITE(KFILX,REC=MREC+K,IOSTAT=IOS,ERR=900)
     1         (RECORD(J),J=NSTART,NEND)
      K=K+1
      IF(K*KSIZE.GE.NSIZE)GO TO 150
      NSTART=K*KSIZE+1
      NREMIN=NREMIN-KSIZE
      GO TO 120
C
 150  IF(K.GT.999)THEN
C           THE MAXIMUM NUMBER OF PHYSICAL RECORDS PER LOGICAL
C           RECORD IS 999.
         WRITE(KFILDO,152)K
 152     FORMAT(/' ****NUMBER OF PHYSICAL RECORDS NECESSARY',
     1           ' FOR WRITING LOGICAL RECORD = ',I7,' EXCEEDS 999.',
     2           '  IER = 150 IN WRDATM.')
         IER=150  
         GO TO 902
      ENDIF
C
CD     WRITE(KFILDO,170)CFROM,MREC
CD170  FORMAT(/,' IN WRDATM FROM',2X,A6,
CD    1         ' RECORD NO. =',I5,/,(' ',9F10.2))
C
      JREC=MAX(JREC,MREC*1000+K)
C        JREC NOW INCLUDES THE NUMBER OF PHYSICAL RECORDS.
C        HOWEVER, THE NUMBER OF PHYSICAL RECORDS REFLECTS THE
C        SPACE RESERVED, NOT NECESSARILY THE ACTUAL NUMBER OF
C        RECORDS USED.  THIS IS INPORTANT ONLY WHEN REPLACING
C        RECORDS OF DIFFERENT SIZES.
      GO TO 902 
C 
 900  WRITE(KFILDO,901)KFILX,CFROM,IOS
 901  FORMAT(/,' ****TROUBLE WRITING DATA RECORD ON UNIT NO. ',I3,
     1         ' IN WRDATM FROM ',A6,'.  IOSTAT = ',I4)
      IER=IOS
C
 902  RETURN
C
      END 