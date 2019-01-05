      subroutine gridij_to_latlon(nx,ny,mproj,xmeshl,orient,xlat,xlatll,
     +                            xlonll,lats,lons,ier)
      implicit none

      integer, intent(in) :: nx
      integer, intent(in) :: ny
      integer, intent(in) :: mproj
      real, intent(in) :: xmeshl
      real, intent(in) :: orient
      real, intent(in) :: xlat
      real, intent(in) :: xlatll
      real, intent(in) :: xlonll
      real, intent(out), dimension(nx,ny) :: lats
      real, intent(out), dimension(nx,ny) :: lons
      integer, intent(out) :: ier

      integer :: i,j
      real :: alat,alon

      ier=0
      alat=0.0
      alon=0.0

      if(mproj.eq.3)then
         do j=1,ny
            do i=1,nx
               call lmijll(6,real(i),real(j),xmeshl,orient,xlat,xlatll,
     +                     xlonll,alat,alon,ier)
               lats(i,j)=alat
               lons(i,j)=alon
            end do
         end do
      elseif(mproj.eq.5)then
         do j=1,ny
            do i=1,nx
               call psijll(6,real(i),real(j),xmeshl,orient,xlat,xlatll,
     +                     xlonll,alat,alon)
               lats(i,j)=alat
               lons(i,j)=alon
            end do
         end do
      elseif(mproj.eq.7)then
         do j=1,ny
            do i=1,nx
               call mcijll(6,real(i),real(j),xmeshl,xlat,xlatll,
     +                     xlonll,alat,alon)
               lats(i,j)=alat
               lons(i,j)=alon
            end do
         end do
      endif

      return
      end subroutine gridij_to_latlon