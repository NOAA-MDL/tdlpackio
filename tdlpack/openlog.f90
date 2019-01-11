subroutine openlog(kstdout,file,ier)
implicit none

integer, intent(in) :: kstdout
character(len=*), intent(in) :: file
integer, intent(out) :: ier

integer :: ios

ios=0

open(unit=kstdout,file=file,form="formatted",status="replace",iostat=ios)
ier=ios

return
end subroutine openlog