      subroutine backspacefile(lun,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(out) :: ier

      integer :: ios

      ier=0
      ios=0

      backspace(lun,iostat=ios)

      ier=ios

      return
      end subroutine backspacefile
      
      subroutine rewindfile(lun,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(out) :: ier

      integer :: ios

      ier=0
      ios=0

      rewind(lun,iostat=ios)

      ier=ios

      return
      end subroutine rewindfile

