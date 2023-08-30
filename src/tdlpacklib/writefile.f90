subroutine writefile(kstdout,file,lun,ftype,nd5,ipack,ier,nreplace,ncheck)
use tdlpacklib_mod
implicit none

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kstdout
character(len=*), intent(in) :: file
integer, intent(in) :: lun
integer, intent(in) :: nd5
integer, intent(in) :: ftype
integer, intent(in), dimension(nd5) :: ipack
integer, intent(out) :: ier
integer, intent(in), optional :: nreplace
integer, intent(in), optional :: ncheck

! ---------------------------------------------------------------------------------------- 
! Local Variables
! ---------------------------------------------------------------------------------------- 
integer :: n,ios,ioctet,ntrash,nsize
integer :: nreplacex,ncheckx
integer, dimension(4) :: id

! ---------------------------------------------------------------------------------------- 
! Initialize
! ---------------------------------------------------------------------------------------- 
ier=0
ios=0
ioctet=nd5*nbypwd
ncheckx=0
nreplacex=0
nsize=0
ntrash=0
id(:)=0

! ---------------------------------------------------------------------------------------- 
! Perform appropriate writing according file type (ftype).
! ---------------------------------------------------------------------------------------- 
if(ftype.eq.1)then
   ! Random-Access
   if(present(nreplace))nreplacex=nreplace
   if(present(ncheck))ncheckx=ncheck
   if(transfer(ipack(1),"    ").eq."TDLP".or.transfer(ipack(1),"    ").eq."PLDT")then
      id(1:4)=ipack(5:8)
   else
      id(1)=400001000
      id(2:4)=0
   endif
   nsize=nd5
   call wrtdlm(kstdout,lun,file,id,ipack,nsize,nreplacex,ncheckx,l3264b,ier)
elseif(ftype.eq.2)then
   ! Sequential
   if(l3264b.eq.32)then
      write(lun,iostat=ios)ntrash,ioctet,(ipack(n),n=1,nd5)
   elseif(l3264b.eq.64)then
      write(lun,iostat=ios)ioctet,(ipack(n),n=1,nd5)
   endif
   ier=ios
endif

return
end subroutine writefile
