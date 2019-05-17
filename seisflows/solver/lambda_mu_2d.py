
import sys

from os.path import basename, join
from seisflows.plugins.io import sem
from seisflows.tools import unix
from seisflows.tools.tools import Struct, exists
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


def getstruct(*args):
    return Struct(zip(sem.mread(*args)))


def map(model, kernels):
    output = Struct()

    vp = model.vp
    vs = model.vs
    rho = model.rho
    kappa = rho*vp**2.
    mu = rho*vs**2.

    output.lame1 = [(1. - (2./3.)*(mu/kappa))*kernels.kappa]
    output.lame2 = [kernels.mu + (2./3.)*(mu/kappa)*kernels.kappa]
    output.rho = [rho]

    return output



class lambda_mu_2d(custom_import('solver', 'elastic2d')):
    """ Adds Lame parameter machinery to SPECFEM2D
    """
    assert PAR.MATERIALS == 'lambda_mu'

    def export_kernels(self, path):
        assert self.mesh_properties.nproc == 1
        iproc = 0

        path = join(path, 'kernels')

        model_parameters = ['rho', 'vp', 'vs']
        kernel_parameters = ['rho', 'kappa', 'mu']

        model = getstruct(self.cwd+'/'+'DATA/', model_parameters, iproc)
        kernels = getstruct(self.cwd+'/'+'OUTPUT_FILES/', kernel_parameters, iproc, suffix='_kernel')

        unix.mkdir(join(path, basename(self.cwd)))
        self.save(join(path, basename(self.cwd)), map(model, kernels), suffix='_kernel')

        

        
