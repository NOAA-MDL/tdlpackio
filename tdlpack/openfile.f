      subroutine openfile(kstdout,file,mode,l3264b,lun,byteorder,ftype,
     +                    ier,ra_maxent,ra_nbytes)
      implicit none

      integer, intent(in) :: kstdout
      character(len=*), intent(in) :: file
      character(len=*), intent(in) :: mode
      integer, intent(in) :: l3264b
      integer, intent(inout) :: byteorder
      integer, intent(inout) :: ftype
      integer, intent(out) :: lun
      integer, intent(out) :: ier
      integer, intent(in), optional :: ra_maxent
      integer, intent(in), optional :: ra_nbytes

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
            call ckraend(kstdout,lun,file,isysend,byteorder,convertx,
     +                   ier)
            ftype=1
         else
            call ckfilend(kstdout,lun,file,isysend,byteorder,convertx,
     +                    ier)
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

         if(ftype.eq.1)then
            if(present(ra_maxent).and.present(ra_nbytes))then
               call createra(kstdout,file,l3264b,lun,ra_maxent,
     +                       ra_nbytes,ier)
               byteorder=1
            endif
         elseif(ftype.eq.2)then
            if(mode.eq."w")cstatus="replace"
            if(mode.eq."x")cstatus="new"
            byteorder=1
            ftype=2
            open(unit=lun,file=file,form="unformatted",
     +           convert="big_endian",status=cstatus,
     +           action=caction,iostat=ios)
         endif

      endif

      ier=ios

      return
      end subroutine openfile
