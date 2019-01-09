      subroutine writefile(file,lun,nd5,l3264b,ftype,ioctet,ipack,ier,
     +                     nreplace,ncheck)
      implicit none

      character(len=*), intent(in) :: file
      integer, intent(in) :: lun
      integer, intent(in) :: nd5
      integer, intent(in) :: l3264b
      integer, intent(in) :: ftype
      integer, intent(in) :: ioctet
      integer, intent(in), dimension(nd5) :: ipack
      integer, intent(out) :: ier
      integer, intent(in), optional :: nreplace
      integer, intent(in), optional :: ncheck

      integer :: n,ios,ntrash,nsize
      integer :: nreplacex,ncheckx
      integer, dimension(4) :: id

      ier=0
      ios=0
      ncheckx=0
      nreplacex=0
      nsize=0
      ntrash=0
      id(:)=0

      if(ftype.eq.1)then
         if(present(nreplace))nreplacex=nreplace
         if(present(ncheck))ncheckx=ncheck
         nsize=(ioctet*8)/l3264b
         if(transfer(ipack(1),"    ").eq."TDLP".or.
     +      transfer(ipack(1),"    ").eq."PLDT")then
            id(1:4)=ipack(5:8)
         else
            id(1)=400001000
            id(2:4)=0
         endif
         call wrtdlm(6,lun,file,id,ipack,nsize,nreplacex,ncheckx,
     +               l3264b,ier)
      elseif(ftype.eq.2)then
         if(l3264b.eq.32)then
            write(lun,iostat=ios)ntrash,ioctet,
     +      (ipack(n),n=1,(ioctet/(l3264b/8)))
         elseif(l3264b.eq.64)then
            write(lun,iostat=ios)ioctet,(ipack(n),n=1,
     +      (ioctet/(l3264b/8)))
         endif
      endif

      ier=ios

      return
      end subroutine writefile
