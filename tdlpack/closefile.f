      subroutine closefile(lun,ftype,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(in) :: ftype
      integer, intent(out) :: ier

      integer :: ios

      ier=0
      
      if(ftype.eq.1)then
         call clfilm(6,lun,ier)
      elseif(ftype.eq.2)then
         close(lun,iostat=ios)
      endif

      ier=ios

      return
      end subroutine closefile
