subroutine unpack_meta_wrapper(nd5,ipack,nd7,is0,is1,is2,is4,ier)
use tdlpacklib_mod
implicit none

integer(kind=4), intent(in) :: nd5
integer(kind=4), intent(in), dimension(nd5) :: ipack
integer(kind=4), intent(in) :: nd7
integer(kind=4), intent(out), dimension(nd7) :: is0
integer(kind=4), intent(out), dimension(nd7) :: is1
integer(kind=4), intent(out), dimension(nd7) :: is2
integer(kind=4), intent(out), dimension(nd7) :: is4
integer(kind=4), intent(out) :: ier

integer(kind=4) :: igive,kfildo
integer(kind=4) :: misspx,misssx

integer(kind=4), allocatable, dimension(:) :: iwork
real(kind=4), allocatable, dimension(:) :: data

ier=0
igive=1
kfildo=6
misspx=9999
misssx=9997

if(allocated(iwork))deallocate(iwork)
allocate(iwork(nd5))
iwork(:)=0

if(allocated(data))deallocate(data)
allocate(data(1))

call unpack(kfildo,ipack,iwork,data,nd5,&
            is0,is1,is2,is4,nd7,misspx,misssx,&
            igive,l3264b,ier)

if(allocated(iwork))deallocate(iwork)
if(allocated(data))deallocate(data)

return
end subroutine unpack_meta_wrapper
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
subroutine unpack_data_wrapper(nd5,ipack,nd7,is0,is1,is2,is4,data,ier)
use tdlpacklib_mod
implicit none

integer(kind=4), intent(in) :: nd5
integer(kind=4), intent(in), dimension(nd5) :: ipack
integer(kind=4), intent(in) :: nd7
integer(kind=4), intent(out), dimension(nd7) :: is0
integer(kind=4), intent(out), dimension(nd7) :: is1
integer(kind=4), intent(out), dimension(nd7) :: is2
integer(kind=4), intent(out), dimension(nd7) :: is4
real(kind=4), intent(out), dimension(nd5) :: data
integer(kind=4), intent(out) :: ier

integer(kind=4) :: igive,kfildo
integer(kind=4) :: misspx,misssx

integer(kind=4), allocatable, dimension(:) :: iwork

ier=0
igive=2
kfildo=6
misspx=9999
misssx=9997

if(allocated(iwork))deallocate(iwork)
allocate(iwork(nd5))
iwork(:)=0

call unpack(kfildo,ipack,iwork,data,nd5,&
            is0,is1,is2,is4,nd7,misspx,misssx,&
            igive,l3264b,ier)

if(allocated(iwork))deallocate(iwork)

return
end subroutine unpack_data_wrapper
