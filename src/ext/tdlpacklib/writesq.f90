subroutine writesq_station_record(kfildo,kfilio,nd5,ipack,ntotby,ntotrc,ier)
use tdlpacklib_mod
implicit none

! ----------------------------------------------------------------------------------------
! Input/Output Variables
! ----------------------------------------------------------------------------------------
integer, intent(in) :: kfildo
integer, intent(in) :: kfilio
integer, intent(in) :: nd5
character(len=8), intent(in), dimension(nd5) :: ipack
integer, intent(inout) :: ntotby
integer, intent(inout) :: ntotrc
integer, intent(out) :: ier

! ----------------------------------------------------------------------------------------
! Local Variables
! ----------------------------------------------------------------------------------------
integer :: n,ios,nbytes,ntrash

! ----------------------------------------------------------------------------------------
! Initialize
! ----------------------------------------------------------------------------------------
ier=0
ios=0
nbytes=nd5*8
ntrash=0

! ----------------------------------------------------------------------------------------
! Update bytes and records totals
! ----------------------------------------------------------------------------------------
ntotby=ntotby+nbytes
ntotrc=ntotrc+1

! ----------------------------------------------------------------------------------------
! Write according to l3264b
! ----------------------------------------------------------------------------------------
if(l3264b.eq.32)then
   write(kfilio,iostat=ios)ntrash,nbytes,(ipack(n),n=1,nd5)
elseif(l3264b.eq.64)then
   write(kfilio,iostat=ios)nbytes,(ipack(n),n=1,nd5)
endif
ier=ios

return
end subroutine writesq_station_record
