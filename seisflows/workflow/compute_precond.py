
from glob import glob

import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import cast, exists
from seisflows.config import , \
    ParameterError

from seisflows.plugins import adjoint

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']
preprocess = sys.modules['seisflows_preprocess']
postprocess = sys.modules['seisflows_postprocess']


class compute_precond(object):
    """ Computes diagonal preconditioner described by Modrak et al 2016
    """

    def check(self):
        """ Checks parameters and paths
        """
        # check paths
        if 'GLOBAL' not in PATH:
            raise ParameterError(PATH, 'GLOBAL')

        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)

        if 'OUTPUT' not in PATH:
            raise ParameterError(PATH, 'OUTPUT')

        # check input
        if 'DATA' not in PATH:
            setattr(PATH, 'DATA', None)

        if 'MODEL_INIT' not in PATH:
            raise ParameterError(PATH, 'MODEL_INIT')

        if 'CLIP' not in PAR:
            setattr(PAR, 'CLIP', 0.)

        # assertions
        0. <= PAR.CLIP <= 1.


    def main(self):
        path = PATH.GLOBAL

        # prepare directory structure
        unix.rm(path)
        unix.mkdir(path)

        # set up workflow machinery
        preprocess.setup()
        postprocess.setup()

        system.run('solver', 'setup',
                   hosts='all')

        print 'Computing preconditioner...'
        system.run('workflow', 'compute_precond',
                   hosts='all',
                   model_path=PATH.MODEL_INIT,
                   model_name='model',
                   model_type='gll')

        postprocess.combine_kernels(
            path=path,
            parameters=solver.parameters)

        for span in cast(PAR.SMOOTH):
            self.process_kernels(
                path=path,
                parameters=solver.parameters,
                span=span)

            # save preconditioner
            src = path +'/'+ 'kernels/absval'
            dst = PATH.OUTPUT +'/'+ 'precond_%04d' % span
            unix.cp(src, dst)

        print 'Finished\n'


    def compute_precond(self, model_path=None, model_name=None, model_type='gll'):
        assert(model_name)
        assert(model_type)
        assert (exists(model_path))

        unix.cd(solver.cwd)

        src = model_path
        dst = solver.model_databases
        solver.save(dst, solver.load(src))

        solver.forward()
        unix.mv(solver.data_wildcard, 'traces/syn')
        solver.initialize_adjoint_traces('traces/syn')
        self.process_traces(solver.cwd)

        solver.adjoint()
        solver.export_kernels(PATH.GLOBAL)


    def process_kernels(self, path, parameters, span):
        assert exists(path)
        assert len(parameters) > 0

        # take absolute value
        parts = solver.load(path +'/'+ 'kernels/sum', suffix='_kernel')
        for key in parameters:
            parts[key] = np.abs(parts[key])

        self._save(path, parts)


        # smooth
        system.run('solver', 'smooth',
                   hosts='head',
                   path=path +'/'+ 'kernels/absval',
                   parameters=parameters,
                   span=span)

        # normalize
        parts = solver.load(path +'/'+ 'kernels/absval', suffix='_kernel')
        for key in parameters:
            parts[key] = np.mean(parts[key])/parts[key]

        self._save(path, parts)



    def _save(self, path, parts):
        solver.save(path +'/'+ 'kernels/absval',
                    parts,
                    suffix='_kernel')


    def _load(path, parameters, prefix='', suffix=''):
        parts = {}
        for key in parameters:
            parts[key] = []

        for iproc in range(solver.mesh.nproc):
            # read database files
            keys, vals = loadbypar(path, parameters, iproc, prefix, suffix)
            for key, val in zip(keys, vals):
                parts[key] += [val]
        return parts


    def process_traces(self, path):
        unix.cd(path)

        d, h = preprocess.load(prefix='traces/obs/')
        s, h = preprocess.load(prefix='traces/syn/')

        s = preprocess.apply(adjoint.precond2, [s, d], [h])

        preprocess.save(s, h, prefix='traces/adj/')

