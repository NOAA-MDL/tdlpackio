      subroutine createra(kstdout,file,l3264b,lun,maxent,nbytes,ier)
      implicit none

      integer, parameter :: NW=140000

      integer, intent(in) :: kstdout
      character(len=*), intent(in) :: file
      integer, intent(in) :: l3264b
      integer, intent(in) :: lun
      integer, intent(in) :: maxent
      integer, intent(in) :: nbytes
      integer, intent(out) :: ier

      integer :: ios
      integer :: lnbytes
      integer, dimension(6) :: master
      integer, dimension(6) :: noprec
      integer, dimension(nw) :: keyr

      ier=0
      ios=0

      keyr(:)=0

      master(1)=0
      master(2)=4
      lnbytes=((nbytes+7)/8)*8
      master(3)=lnbytes/(l3264b/8)
      master(4)=1
      master(5)=max(maxent,((lnbytes*8/l3264b)-3)/6)
      master(6)=2

      noprec(1)=0
      noprec(2)=2
      noprec(3)=0
      noprec(4)=0
      noprec(5)=0
      noprec(6)=99999999

      open(unit=lun,file=file,status="new",convert="big_endian",
     +     access="direct",recl=nbytes,iostat=ios)

      write(lun,rec=1,iostat=ios)master

      call wrkeym(kstdout,lun,noprec,keyr,master(5)*6+3,master(3),
     +            "      ",ier)

      close(lun,iostat=ios)

      return
      end subroutine createra