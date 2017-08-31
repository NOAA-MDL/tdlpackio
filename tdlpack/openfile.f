      subroutine openfile(file,mode,lun,byteorder,ftype)
      implicit none

      character(len=*), intent(in) :: file
      character(len=*), intent(in) :: mode
      integer, intent(out) :: lun
      integer, intent(out) :: byteorder
      integer, intent(out) :: ftype

      integer :: ier,ios,itemp
      character(len=:), allocatable :: cstatus
      character(len=20) :: convertx

      integer, save :: ienter=0
      integer, save :: isysend=0
      integer, save :: lunx=65535

      if(ienter.eq.0)call cksysend(6,"     ",isysend,ier)

      lun=lunx

      if(mode.eq."r".or.mode.eq."a")then
         if(mode.eq."r")cstatus="old"
         if(mode.eq."a")cstatus="append"

         open(unit=lun,file=file,form="unformatted",access="stream",
     +        status="old",iostat=ios)
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
      elseif(mode.eq."w")then
         cstatus="replace"
         open(unit=lun,file=file,form="unformatted",
     +        convert="big_endian",status=cstatus,iostat=ios)
      endif

      lunx=lunx-1

      return
      end subroutine openfile
