subroutine writera(kfildo,kfilx,cfilx,id,nd5,ipack,nrepla,ncheck,ier)
implicit none

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kfildo
integer, intent(in) :: kfilx
character(len=*), intent(in) :: cfilx
integer, intent(in), dimension(4) :: id
integer, intent(in) :: nd5
integer, intent(in), dimension(nd5) :: ipack
integer, intent(in) :: nrepla
integer, intent(in) :: ncheck
integer, intent(out) :: ier

! ---------------------------------------------------------------------------------------- 
! Local Variables
! ---------------------------------------------------------------------------------------- 
integer :: l3264b

! ---------------------------------------------------------------------------------------- 
! Initialize
! ---------------------------------------------------------------------------------------- 
l3264b=32

! ---------------------------------------------------------------------------------------- 
! Call WRTDLM
! ---------------------------------------------------------------------------------------- 
call wrtdlm(kfildo,kfilx,cfilx,id,ipack,nd5,nrepla,ncheck,l3264b,ier)

return
end subroutine writera
