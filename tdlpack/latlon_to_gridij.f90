subroutine latlon_to_gridij(kstdout,mproj,xlatll,xlonll,orient,xmeshl,xlat,alat,alon,xi,yj)
implicit none

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kstdout
integer, intent(in) :: mproj
real, intent(in) :: xlatll
real, intent(in) :: xlonll
real, intent(in) :: orient
real, intent(in) :: xmeshl
real, intent(in) :: xlat
real, intent(in) :: alat
real, intent(in) :: alon
real, intent(out) :: xi
real, intent(out) :: yj

! ---------------------------------------------------------------------------------------- 
! Call appropriate map projection-specific subroutine to convert lat,lon to i,j.
! ---------------------------------------------------------------------------------------- 
if(mproj.eq.3)then
   ! Lambert Conformal
   call lmllij(kstdout,alat,alon,xmeshl,orient,xlat,xlatll,xlonll,xi,yj)
elseif(mproj.eq.5)then
   ! Polar Stereographic
   call psllij(kstdout,alat,alon,xmeshl,orient,xlat,xlatll,xlonll,xi,yj)
elseif(mproj.eq.7)then
   ! Mercator
   call mcllij(kstdout,alat,alon,xmeshl,xlat,xlatll,xlonll,xi,yj)
endif

return
end subroutine latlon_to_gridij
