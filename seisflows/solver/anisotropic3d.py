
from os.path import join

from seisflows.plugins.io import copybin, loadbypar, savebin, splitvec, Minmax
from seisflows.plugins.io import Model as IOStruct

from seisflows.tools import unix
from seisflows.tools.tools import exists
from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']



class anisotropic3d(custom_import('solver', 'elastic'), custom_import('solver', 'specfem3d')):
    raise NotImplementedError
