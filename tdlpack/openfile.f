      subroutine openfile(file,mode,lun,byteorder,ftype,ier)
      implicit none

      character(len=*), intent(in) :: file
      character(len=*), intent(in) :: mode
      integer, intent(out) :: lun
      integer, intent(out) :: byteorder
      integer, intent(out) :: ftype
      integer, intent(out) :: ier

      integer :: ios,itemp
      character(len=:), allocatable :: cstatus
      character(len=20) :: convertx

      integer, save :: ienter=0
      integer, save :: isysend=0
      integer, save :: lunx=65535

      ier=0
      ios=0

      if(ienter.eq.0)call cksysend(6,"     ",isysend,ier)
      lun=lunx+ienter
      ienter=ienter+1

      if(mode.eq."r".or.mode.eq."a")then
         if(mode.eq."r")cstatus="old"
         if(mode.eq."a")cstatus="append"

         open(unit=lun,file=file,form="unformatted",access="stream",
     +        status=cstatus,iostat=ios)
         read(lun,iostat=ios)itemp
         close(lun)

         if(itemp.eq.0)then
            call ckraend(6,lun,file,isysend,byteorder,convertx,ier)
            ftype=1
         else
            call ckfilend(6,lun,file,isysend,byteorder,convertx,ier)
            ftype=2
            open(unit=lun,file=file,form="unformatted",
     +           convert="big_endian",status=cstatus,iostat=ios)
         endif
      elseif(mode.eq."w".or.mode.eq."x")then
         if(mode.eq."w")cstatus="replace"
         if(mode.eq."x")cstatus="new"
         byteorder=1
         ftype=2
         open(unit=lun,file=file,form="unformatted",
     +        convert="big_endian",status=cstatus,iostat=ios)
      endif

      ier=ios

      return
      end subroutine openfile
