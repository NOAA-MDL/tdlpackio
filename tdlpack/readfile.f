      subroutine readfile(file,lun,nd5,l3264b,ftype,ioctet,ipack,ier,id)
      implicit none

      character(len=*), intent(in) :: file
      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer, intent(in) :: l3264b
      integer, intent(in) :: ftype
      integer, intent(out) :: ioctet
      integer, intent(out), dimension(nd5) :: ipack
      integer, intent(out) :: ier
      integer, intent(in), dimension(4), optional :: id

      integer :: n,ios,ntrash,nvalue

      ier=0
      ios=0
      ntrash=0
      nvalue=0

      if(ftype.eq.1)then
         call rdtdlm(6,lun,file,id,ipack,nd5,nvalue,l3264b,ier)
         ioctet=nvalue*(l3264b/8)
         if(ier.eq.153)ios=-1
      elseif(ftype.eq.2)then
         if(l3264b.eq.32)then
            read(lun,iostat=ios)ntrash,ioctet,
     +      (ipack(n),n=1,(ioctet/(l3264b/8)))
         elseif(l3264b.eq.64)then
            read(lun,iostat=ios)ioctet,(ipack(n),n=1,
     +      (ioctet/(l3264b/8)))
         endif
      endif

      ier=ios

      return
      end subroutine readfile
