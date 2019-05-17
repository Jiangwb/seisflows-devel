
from glob import glob
from os.path import join

from seisflows.tools import unix

from seisflows.plugins.io import copybin, savebin
from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']


class Thomsen_base(custom_import('solver', 'specfem3d_legacy')):

    #raise NotImplementedError("Need to fix xsum_kernels utility".)

    # parameters expected by solver
    solver_parameters = []
    solver_parameters += ['vp']
    solver_parameters += ['vs']
    solver_parameters += ['epsilon']
    solver_parameters += ['delta']
    solver_parameters += ['gamma']
    solver_parameters += ['theta']
    solver_parameters += ['azimuth']


    def save(self, path, model, prefix='', suffix=''):
        super(Thomsen_base, self).save(
            path, model, prefix, suffix, self.solver_parameters)


    def export_model(self, path):
        super(Thomsen_base, self).export_model(
            path, self.solver_parameters+['rho'])


