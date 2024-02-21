subroutine openfile(kstdout,file,mode,lun,byteorder,ftype,ier,ra_template)
implicit none

! ---------------------------------------------------------------------------------------- 
! Input/Output Variables
! ---------------------------------------------------------------------------------------- 
integer, intent(in) :: kstdout
character(len=*), intent(in) :: file
character(len=*), intent(in) :: mode
integer, intent(inout) :: byteorder
integer, intent(inout) :: ftype
integer, intent(out) :: lun
integer, intent(out) :: ier
character(len=*), intent(in), optional :: ra_template

! ---------------------------------------------------------------------------------------- 
! Local Variables
! ---------------------------------------------------------------------------------------- 
integer :: ios,itemp
integer :: l3264b,maxent,nbytes
character(len=1) :: mode1
character(len=:), allocatable :: caccess
character(len=:), allocatable :: caction
character(len=:), allocatable :: cstatus
character(len=20) :: convertx

integer, save :: ienter=0
integer, save :: isysend=0
integer, save :: lunx=65535

! ---------------------------------------------------------------------------------------- 
! Initialize
! ---------------------------------------------------------------------------------------- 
ier=0
ios=0
l3264b=32
mode1=mode(1:1)
caccess=""
caction="readwrite"
cstatus=""

! ---------------------------------------------------------------------------------------- 
! Get byte order of the system and set unit number.
! ---------------------------------------------------------------------------------------- 
if(ienter.eq.0)call cksysend(6,"     ",isysend,ier)
lun=lunx+ienter
ienter=ienter+1

! ---------------------------------------------------------------------------------------- 
! Perform the following for read (only) and append (can be read and/or write).
! ---------------------------------------------------------------------------------------- 
if(mode1.eq."r".or.mode1.eq."a")then

   ! Open file for stream access; read first 4 bytes; close.
   open(unit=lun,file=file,form="unformatted",access="stream",status="old",iostat=ios)
   read(lun,iostat=ios)itemp
   close(lun)

   ! Test itemp to determine if file is random-access or sequential; then perform
   ! appropriate IO action to prepare for reading the file.
   if(itemp.eq.0)then
      ! Random-Access
      call ckraend(kstdout,lun,file,isysend,byteorder,convertx,ier)
      ftype=1
   else
      ! Sequential
      call ckfilend(kstdout,lun,file,isysend,byteorder,convertx,ier)
      ftype=2
      cstatus="old"
      if(mode1.eq."r")then
         caccess="sequential"
         caction="read"
      elseif(mode1.eq."a")then
         caccess="append"
      endif
      open(unit=lun,file=file,form="unformatted",convert="big_endian",status=cstatus,&
           iostat=ios,access=caccess,action=caction)
      ier=ios
   endif

! ---------------------------------------------------------------------------------------- 
! Perform the following for new files.
! ---------------------------------------------------------------------------------------- 
elseif(mode1.eq."w".or.mode1.eq."x")then

   if(ftype.eq.1)then
      ! Random-Access
      if(present(ra_template))then
         if(ra_template.eq."small")then
            maxent=300
            nbytes=2000
         elseif(ra_template.eq."large")then
            maxent=840
            nbytes=20000
         endif
         call createra(kstdout,file,l3264b,lun,maxent,nbytes,ier)
         byteorder=1
      endif
   elseif(ftype.eq.2)then
      ! Sequential
      if(mode1.eq."w")cstatus="replace"
      if(mode1.eq."x")cstatus="new"
      byteorder=1
      ftype=2
      open(unit=lun,file=file,form="unformatted",convert="big_endian",status=cstatus,&
           action=caction,iostat=ios)
      ier=ios
   endif

endif

return
end subroutine openfile
