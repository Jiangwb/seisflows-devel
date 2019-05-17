
from os.path import join

from seisflows.plugins.io import copybin, loadbypar, savebin, splitvec, Minmax
from seisflows.plugins.io import Model as IOStruct

from seisflows.tools import unix
from seisflows.tools.tools import exists
from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']



class anisotropic(custom_import('solver', 'elastic')):
    """ Adds elastic inversion machinery
    """
    model_parameters = []
    model_parameters += ['c11']
    model_parameters += ['c13']
    model_parameters += ['c15']
    model_parameters += ['c33']
    model_parameters += ['c35']
    model_parameters += ['c55']


    if PAR.MATERIALS == 'ChenTromp2d':
        from seisflows.plugins.maps import voigt_chentromp_2d as map_forward
        from seisflows.plugins.maps import chentromp_voigt_2d as map_inverse
        kernel_parameters = []
        kernel_parameters += ['A']
        kernel_parameters += ['C']
        kernel_parameters += ['N']
        kernel_parameters += ['L']
        kernel_parameters += ['F']


    elif PAR.MATERIALS == 'Voigt2d':
        from seisflows.plugins.maps import voigt_voigt_2d as map_forward
        from seisflows.plugins.maps import voigt_voigt_2d as map_inverse
        kernel_parameters = []
        kernel_parameters += ['c11']
        kernel_parameters += ['c13']
        kernel_parameters += ['c15']
        kernel_parameters += ['c33']
        kernel_parameters += ['c35']
        kernel_parameters += ['c55']


    elif PAR.MATERIALS == 'Thomsen2d':
        from seisflows.plugins.maps import voigt_thomsen_2d as map_forward
        from seisflows.plugins.maps import thomsen_voigt_2d as map_inverse
        kernel_parameters = []
        kernel_parameters += ['vp']
        kernel_parameters += ['vs']
        kernel_parameters += ['epsilon']
        kernel_parameters += ['delta']
        kernel_parameters += ['gamma']
        kernel_parameters += ['theta']

    else:
        raise ParameterError(PAR, 'MATERIALS')



