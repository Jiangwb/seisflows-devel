import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.tools import loadtxt, savetxt
from seisflows.config import , ParameterError, custom_import

from seisflows.optimize import lib

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class gauss_newton(custom_import('optimize', 'newton')):
    """ Implements Gauss-Newton-CG algorithm
    """

    def check(cls):
        """ Checks parameters and paths
        """
        super(gauss_newton, cls).check()


    def hessian_product(cls, h):
        return self.load('g_lcg')/h
