      subroutine readfile(lun,nd5,ipack,ioctet,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer, intent(out), dimension(nd5) :: ipack
      integer(kind=8), intent(out) :: ioctet
      integer, intent(out) :: ier

      integer :: n,ios

      ier=0
      ios=0

      read(lun,iostat=ios)ioctet,(ipack(n),n=1,ioctet/4)

      ier=ios

      return
      end subroutine readfile
!
!
!
      subroutine writefile(lun,nd5,ioctet,ipack,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer(kind=8), intent(in) :: ioctet
      integer, intent(in), dimension(nd5) :: ipack
      integer, intent(out) :: ier

      integer :: n,ios

      ier=0
      ios=0

      write(lun,iostat=ios)ioctet,(ipack(n),n=1,ioctet/4)

      ier=ios

      return
      end subroutine writefile
