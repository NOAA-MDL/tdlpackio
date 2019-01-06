      subroutine openfile(file,mode,lun,byteorder,ftype,ier)
      implicit none

      character(len=*), intent(in) :: file
      character(len=*), intent(in) :: mode
      integer, intent(out) :: lun
      integer, intent(out) :: byteorder
      integer, intent(out) :: ftype
      integer, intent(out) :: ier

      integer :: ios,itemp
      character(len=:), allocatable :: caccess
      character(len=:), allocatable :: caction
      character(len=:), allocatable :: cstatus
      character(len=20) :: convertx

      integer, save :: ienter=0
      integer, save :: isysend=0
      integer, save :: lunx=65535

      ier=0
      ios=0
      caction="readwrite"

      if(ienter.eq.0)call cksysend(6,"     ",isysend,ier)
      lun=lunx+ienter
      ienter=ienter+1

      if(mode.eq."r".or.mode.eq."a")then

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
            cstatus="old"
            if(mode.eq."r")then
               caccess="sequential"
               caction="read"
            elseif(mode.eq."a")then
               caccess="append"
            endif
            open(unit=lun,file=file,form="unformatted",
     +           convert="big_endian",status=cstatus,iostat=ios,
     +           access=caccess,action=caction)
         endif

      elseif(mode.eq."w".or.mode.eq."x")then

         if(mode.eq."w")cstatus="replace"
         if(mode.eq."x")cstatus="new"
         byteorder=1
         ftype=2
         open(unit=lun,file=file,form="unformatted",
     +        convert="big_endian",status=cstatus,
     +        action=caction,iostat=ios)

      endif

      ier=ios

      return
      end subroutine openfile
