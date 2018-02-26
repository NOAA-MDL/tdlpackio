      subroutine x1dto2d(nx,ny,nxy,datain,dataout,ier)
      implicit none

      integer, intent(in) :: nx
      integer, intent(in) :: ny
      integer, intent(in) :: nxy
      real, intent(in), dimension(nxy) :: datain
      real, intent(out), dimension(nx,ny) :: dataout
      integer, intent(out) :: ier

      integer :: i,j,ij

      do j=1,ny
         do i=1,nx
            ij=(nx*(j-1))+i
            dataout(i,j)=datain(ij)
         end do
      end do

      return
      end subroutine x1dto2d
C ---------------------------------------------------------------------- 
C ---------------------------------------------------------------------- 
C ---------------------------------------------------------------------- 
C ---------------------------------------------------------------------- 
      subroutine x2dto1d(nx,ny,nxy,datain,dataout,ier)
      implicit none

      integer, intent(in) :: nx
      integer, intent(in) :: ny
      integer, intent(in) :: nxy
      real, intent(in), dimension(nx,ny) :: datain
      real, intent(out), dimension(nxy) :: dataout
      integer, intent(out) :: ier

      integer :: i,j,ij

      do j=1,ny
         do i=1,nx
            ij=(nx*(j-1))+i
            dataout(ij)=datain(i,j)
         end do
      end do

      return
      end subroutine x2dto1d
