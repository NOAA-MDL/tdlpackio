      subroutine readfile(lun,nd5,l3264b,ipack,ioctet,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer, intent(in) :: l3264b
      integer, intent(out), dimension(nd5) :: ipack
      integer, intent(out) :: ioctet
      integer, intent(out) :: ier

      integer :: n,ios,ntrash

      ier=0
      ios=0
      ntrash=0

      if(l3264b.eq.32)then
         read(lun,iostat=ios)ntrash,ioctet,
     1   (ipack(n),n=1,(ioctet/(l3264b/8)))
      elseif(l3264b.eq.64)then
         read(lun,iostat=ios)ioctet,(ipack(n),n=1,(ioctet/(l3264b/8)))
      endif

      ier=ios

      return
      end subroutine readfile
!
!
!
      subroutine writefile(lun,nd5,l3264b,ioctet,ipack,ier)
      implicit none

      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer, intent(in) :: l3264b
      integer, intent(in) :: ioctet
      integer, intent(in), dimension(nd5) :: ipack
      integer, intent(out) :: ier

      integer :: n,ios,ntrash

      ier=0
      ios=0
      ntrash=0

      if(l3264b.eq.32)then
         write(lun,iostat=ios)ntrash,ioctet,
     1   (ipack(n),n=1,(ioctet/(l3264b/8)))
      elseif(l3264b.eq.64)then
         write(lun,iostat=ios)ioctet,(ipack(n),n=1,(ioctet/(l3264b/8)))
      endif

      ier=ios

      return
      end subroutine writefile
