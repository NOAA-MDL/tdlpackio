subroutine closefile(kstdout,lun,ftype,ier)
implicit none

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kstdout
integer, intent(in) :: lun
integer, intent(in) :: ftype
integer, intent(out) :: ier

! ---------------------------------------------------------------------------------------- 
! Local Variables
! ---------------------------------------------------------------------------------------- 
integer :: ios

! ---------------------------------------------------------------------------------------- 
! Initialize
! ---------------------------------------------------------------------------------------- 
ier=0

! ---------------------------------------------------------------------------------------- 
! Close file according to ftype
! ---------------------------------------------------------------------------------------- 
if(ftype.eq.1)then
   ! Random-Access
   call clfilm(kstdout,lun,ier)
elseif(ftype.eq.2)then
   ! Sequential
   close(lun,iostat=ios)
   ier=ios
endif

return
end subroutine closefile
