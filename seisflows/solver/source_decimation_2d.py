
from glob import glob
from os.path import basename, join

import numpy as np

from seisflows.tools import unix

from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']


class source_decimation_2d(custom_import('solver', 'source_decimation'), custom_import('solver', 'specfem2d')):
    """ Adds source_decimation machinery to SPECFEM2D
    """
    pass
