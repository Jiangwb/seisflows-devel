
from glob import glob
from os.path import join

from seisflows.tools import unix

from seisflows.plugins.io import copybin, savebin
from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']


class ChenTromp_base(custom_import('solver', 'specfem3d_legacy')):

    # model parameters expected by solver
    solver_parameters = []
    solver_parameters += ['A']
    solver_parameters += ['C']
    solver_parameters += ['N']
    solver_parameters += ['L']
    solver_parameters += ['F']
    solver_parameters += ['Jc']
    solver_parameters += ['Js']
    solver_parameters += ['Kc']
    solver_parameters += ['Ks']
    solver_parameters += ['Mc']
    solver_parameters += ['Ms']
    solver_parameters += ['Gc']
    solver_parameters += ['Gs']
    solver_parameters += ['Bc']
    solver_parameters += ['Bs']
    solver_parameters += ['Hc']
    solver_parameters += ['Hs']
    solver_parameters += ['Dc']
    solver_parameters += ['Ds']
    solver_parameters += ['Ec']
    solver_parameters += ['Es']


    def save(self, path, model, prefix='', suffix=''):
        super(ChenTromp_base, self).save(
            path, model, prefix, suffix, self.solver_parameters)

    def export_model(self, path):
        super(ChenTromp_base, self).export_model(
            path, self.solver_parameters+['rho'])

