
from seisflows.config import custom_import

class elastic2d(custom_import('solver', 'elastic'), custom_import('solver', 'specfem2d')):
    """ Adds elastic inversion machinery to SPECFEM2D
    """
    pass

