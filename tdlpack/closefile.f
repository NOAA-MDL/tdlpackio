      subroutine closefile(lun,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(out) :: ier

      integer :: ios

      ier=0

      close(lun,iostat=ios)

      ier=ios

      return
      end subroutine closefile
