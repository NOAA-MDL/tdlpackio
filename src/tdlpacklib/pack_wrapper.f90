subroutine pack1d_wrapper(nd7,is0,is1,is2,is4,nd,data,nd5,ipack,ioctet,ier)
implicit none

integer(kind=4), intent(in) :: nd7
integer(kind=4), intent(in), dimension(nd7) :: is0
integer(kind=4), intent(in), dimension(nd7) :: is1
integer(kind=4), intent(in), dimension(nd7) :: is2
integer(kind=4), intent(in), dimension(nd7) :: is4
integer(kind=4), intent(in) :: nd
real(kind=4), intent(in), dimension(nd) :: data
integer(kind=4), intent(in) :: nd5
integer(kind=4), intent(out), dimension(nd5) :: ipack
integer(kind=4), intent(out) :: ioctet
integer(kind=4), intent(out) :: ier

integer(kind=4) :: kfildo,l3264b,lx,minpk
real(kind=4) :: xmissp,xmisss

integer(kind=4), allocatable, dimension(:) :: ic

ier=0
ioctet=0
kfildo=6
l3264b=storage_size(nd5)
lx=0
minpk=21
xmissp=real(is4(4))
xmisss=real(is4(5))

if(allocated(ic))deallocate(ic)
allocate(ic(nd5))
ic(:)=0

call pack1d(kfildo,data,ic,nd,is0,is1,is2,is4,&
            nd7,xmissp,xmisss,ipack,nd5,&
            minpk,lx,ioctet,l3264b,ier)

if(allocated(ic))deallocate(ic)

return
end subroutine pack1d_wrapper
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
subroutine pack2d_wrapper(nd7,is0,is1,is2,is4,nx,ny,data,nd5,ipack,ioctet,ier)
implicit none

integer(kind=4), intent(in) :: nd7
integer(kind=4), intent(in), dimension(nd7) :: is0
integer(kind=4), intent(in), dimension(nd7) :: is1
integer(kind=4), intent(in), dimension(nd7) :: is2
integer(kind=4), intent(in), dimension(nd7) :: is4
integer(kind=4), intent(in) :: nx
integer(kind=4), intent(in) :: ny
real(kind=4), intent(in), dimension(nx,ny) :: data
integer(kind=4), intent(in) :: nd5
integer(kind=4), intent(out), dimension(nd5) :: ipack
integer(kind=4), intent(out) :: ioctet
integer(kind=4), intent(out) :: ier

integer(kind=4) :: kfildo,l3264b,lx,minpk
real(kind=4) :: xmissp,xmisss

integer(kind=4), allocatable, dimension(:) :: ic
integer(kind=4), allocatable, dimension(:,:) :: ia

ier=0
ioctet=0
kfildo=6
l3264b=storage_size(nd5)
lx=0
minpk=21
xmissp=real(is4(4))
xmisss=real(is4(5))

if(allocated(ia))deallocate(ia)
allocate(ia(nx,ny))
ia(:,:)=0
if(allocated(ic))deallocate(ic)
allocate(ic(nd5))
ic(:)=0

call pack2d(kfildo,data,ia,ic,nx,ny,is0,is1,is2,is4,&
            nd7,xmissp,xmisss,ipack,nd5,&
            minpk,lx,ioctet,l3264b,ier)

if(allocated(ia))deallocate(ia)
if(allocated(ic))deallocate(ic)

return
end subroutine pack2d_wrapper
