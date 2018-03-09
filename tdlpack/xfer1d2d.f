      subroutine xfer1d2d(nx,ny,datain,dataout)
      implicit none

      integer, intent(in) :: nx
      integer, intent(in) :: ny
      real, intent(in), dimension(nx*ny) :: datain
      real, intent(out), dimension(nx,ny) :: dataout

      !dataout=transfer(datain,dataout)
      dataout=reshape(datain,(/nx,ny/))

      return
      end subroutine xfer1d2d
!
!
      subroutine xfer2d1d(nx,ny,datain,dataout)
      implicit none

      integer, intent(in) :: nx
      integer, intent(in) :: ny
      real, intent(in), dimension(nx,ny) :: datain
      real, intent(out), dimension(nx*ny) :: dataout

      !dataout=transfer(datain,dataout)
      dataout=reshape(datain,(/nx*ny/))

      return
      end subroutine xfer2d1d
