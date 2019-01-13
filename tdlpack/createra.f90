subroutine createra(kstdout,file,l3264b,lun,maxent,nbytes,ier)
implicit none

! ---------------------------------------------------------------------------------------- 
! Parameters
!
!    NW = Set to some number sucht hat NW >= nbytes*6 as it is used as the dumension for
!         keyr( ) for writing a blank key record.
! ---------------------------------------------------------------------------------------- 
integer, parameter :: NW=140000

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kstdout
character(len=*), intent(in) :: file
integer, intent(in) :: l3264b
integer, intent(in) :: lun
integer, intent(in) :: maxent
integer, intent(in) :: nbytes
integer, intent(out) :: ier

! ---------------------------------------------------------------------------------------- 
! Locatal Variables
! ---------------------------------------------------------------------------------------- 
integer :: ios
integer :: nbytesx
integer, dimension(6) :: master
integer, dimension(6) :: noprec
integer, dimension(nw) :: keyr

! ---------------------------------------------------------------------------------------- 
! Initialized
! ---------------------------------------------------------------------------------------- 
ier=0
ios=0
nbytesx=0
keyr(:)=0
master(:)=0

! ---------------------------------------------------------------------------------------- 
! Generate master key record
! ---------------------------------------------------------------------------------------- 
nbytesx=((nbytes+7)/8)*8
master(1)=0
master(2)=4
master(3)=nbytesx/(l3264b/8)
master(4)=1
master(5)=max(maxent,((nbytesx*8/l3264b)-3)/6)
master(6)=2

! ---------------------------------------------------------------------------------------- 
! Define array to hold information for key and physical records.
! ---------------------------------------------------------------------------------------- 
noprec(1)=0
noprec(2)=2
noprec(3)=0
noprec(4)=0
noprec(5)=0
noprec(6)=99999999

! ---------------------------------------------------------------------------------------- 
! Open new random access file and write the master key record.
! ---------------------------------------------------------------------------------------- 
open(unit=lun,file=file,status="new",convert="big_endian",access="direct",recl=nbytes,&
     iostat=ios)
ier=ios
if(ier.eq.0)write(lun,rec=1,iostat=ios)master
ier=ios

! ---------------------------------------------------------------------------------------- 
! Write the first key record and close the file.
! ---------------------------------------------------------------------------------------- 
if(ier.eq.0)call wrkeym(kstdout,lun,noprec,keyr,master(5)*6+3,master(3),"      ",ier)
if(ier.eq.0)close(lun,iostat=ios)
ier=ios

return
end subroutine createra