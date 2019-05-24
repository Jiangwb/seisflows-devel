(1) Choose desired mesh discretization

Choose length of and number of elements along x-axis by modifying nx, xmin, xmax in DATA/Par_file.

Choose length of and number of elements along z-axis by modifying DATA/interfaces.dat

(2) output SPECFEM2D mesh coordinates

Specify a homogenous or water-layer-over-halfspace model using nbmodels, nbregions and associated parameters in DATA/Par_file

Choose the following settings in DATA/Par_file

MODEL = default
SAVE_MODEL = ascii
Run mesher and solver.
bin/xmeshfem2D
bin/xspecfem3D

(3) After running the mesher and solver, there should be ascii file(s) DATA/proc******_rho_vp_vs.dat. The first two columns of this file specify the x and z coordinates of the mesh. Interpolate your values for vp,vp,rho onto these coordinates.

(4) Write interpolated values obtained from the previous step in fortran binary format. To do this you'll need a short Fortran program, such as the one in the folder: ./specfem2d_2layers/DATA/xascii_to_binary.f90.

(5) If you want, plot the newly created .bin files to make sure everything look alright (see issue #34). To use your binary files, don't forget to change back the settings in DATA/Par_file:

MODEL = binary
SAVE_MODEL = default

To generate the simple binary model. just cd to specfem2d_2_layers and run run_this_example***.sh. You will get the DATA/proc******_rho_vp_vs.dat, then run xascii_to_binary.f90(use gfortran to compile it) to convert to binary file.
