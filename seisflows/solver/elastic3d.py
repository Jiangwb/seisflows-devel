
from seisflows.config import custom_import

class elastic3d(custom_import('solver', 'elastic'), custom_import('solver', 'specfem3d')):
    """ Adds elastic inversion machinery to SPECFEM2D
    """
    pass

