! XASCII_TO_BINARY
!
! USAGE
!   xascii_to_binary INPUT_FILE OUTPUT_DIR
!

program sum_kernels

  implicit none

  logical, parameter :: USE_RHO_VP_VS = .true.

  integer, parameter :: CUSTOM_REAL = 4
  integer, parameter :: MAX_STRING_LEN = 255

  integer :: ipath, npath, iker, nline, i,j
  real(kind=CUSTOM_REAL), allocatable, dimension(:) :: kernel1, kernel2, kernel3
  real(kind=CUSTOM_REAL), allocatable, dimension(:) :: xcoord, zcoord
  character(len=MAX_STRING_LEN) :: input_file, output_dir
  character(len=MAX_STRING_LEN) :: arg(2), filename
  integer :: ios, ier

  print *, 'Running XASCII_TO_BINARY'
  print *,

  if (command_argument_count() /= 2) then
      print *, 'USAGE: ascii_to_binary INPUT_FILE OUTPUT_DIR'
      print *, ''
      stop 'Please check command line arguments'
  endif

  ! parse command line arguments
  do i = 1, 2
    call get_command_argument(i,arg(i), status=ier)
  enddo
  read(arg(1),'(a)') input_file
  read(arg(2),'(a)') output_dir

  call get_number_lines(input_file, nline)
  print *, 'Number of lines: ', nline
  print *,

  allocate( xcoord(nline) )
  allocate( zcoord(nline) )
  allocate( kernel1(nline) )
  allocate( kernel2(nline) )
  allocate( kernel3(nline) )
  xcoord(:) = 0.d0
  zcoord(:) = 0.d0
  kernel1(:) = 0.00
  kernel2(:) = 0.00
  kernel3(:) = 0.00

  open(unit=100,file=trim(input_file),status='old',action='read')
  do j=1,nline
     read(100,*) xcoord(j), zcoord(j), kernel1(j),  kernel2(j), kernel3(j)
  enddo
  close(100)

 i=0

  write(filename,'(a,i6.6,a)') '/proc', i, '_x.bin'
  open(unit=101, file=trim(output_dir)//trim(filename),status='unknown',action='write',form='unformatted')

  write(filename,'(a,i6.6,a)') '/proc', i, '_z.bin'
  open(unit=102,file=trim(output_dir)//trim(filename),status='unknown',action='write',form='unformatted')

  if (USE_RHO_VP_VS) then
    write(filename,'(a,i6.6,a)') '/proc', i, '_rho.bin'
    open(unit=103,file=trim(output_dir)//trim(filename),status='unknown',action='write',form='unformatted')

    write(filename,'(a,i6.6,a)') '/proc', i, '_vp.bin'
    open(unit=104,file=trim(output_dir)//trim(filename),status='unknown',action='write',form='unformatted')

    write(filename,'(a,i6.6,a)') '/proc', i, '_vs.bin'
    open(unit=105,file=trim(output_dir)//trim(filename),status='unknown',action='write',form='unformatted')
  endif

  print *, 'Writing kernels to: ', trim(output_dir)
  print *,

  write(101) xcoord
  write(102) zcoord
  write(103) kernel1
  write(104) kernel2
  write(105) kernel3

  close(101)
  close(102)
  close(103)
  close(104)
  close(105)

  print *, 'Finished writing kernels '
  print *,

end program sum_kernels


! ------------------------------------------------------------------------------


subroutine get_number_lines(filename, nline)

  integer, parameter :: CUSTOM_REAL = 4
  integer, parameter :: MAX_STRING_LEN = 255
  integer, parameter :: MAX_NUMBER_LINES = 2147483647

  real(kind=CUSTOM_REAL) :: dummy1, dummy2, dummy3, dummy4, dummy5

  character(len=MAX_STRING_LEN) :: filename

  integer :: ios, nline

  print *, trim(filename)

  open(unit=100,file=trim(filename),status='old',action='read')
  nline = 0
  do j=1,MAX_NUMBER_LINES
     read(100,*,iostat=ios) dummy1, dummy2, dummy3, dummy4, dummy5
     if (ios /= 0) exit
     nline=nline+1
  enddo
  close(100)

end subroutine get_number_lines
