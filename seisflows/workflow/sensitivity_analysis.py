
from glob import glob
from os.path import join

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


class sensitivity_analysis(object):

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

        if 'MODEL' not in PATH:
            raise ParameterError(PATH, 'MODEL')

        if 'PERTURB' not in PATH:
            raise ParameterError(PATH, 'PERTURB')

        if 'MODEL_INIT' not in PATH:
            setattr(PATH, 'MODEL_INIT', PATH.MODEL)

        if 'MODEL_TRUE' not in PATH:
            setattr(PATH, 'MODEL_TRUE', PATH.MODEL)


    def main(self):
        """ Computes point spread from a peturbation dm with respect to a
          refrence model m
        """
        self.setup()

        m = solver.merge(solver.load(PATH.MODEL))
        dm = solver.merge(solver.load(PATH.PERTURB))

        path1 = join(PATH.GLOBAL, 'eval1')
        path2 = join(PATH.GLOBAL, 'eval2')

        self.evaluate_gradient(m+dm, path1)
        self.evaluate_gradient(m-dm, path2)

        path1 = join(PATH.GLOBAL, 'eval1', 'gradient')
        path2 = join(PATH.GLOBAL, 'eval2', 'gradient')

        grad1 = solver.merge(solver.load(path1, suffix='_kernel'))
        grad2 = solver.merge(solver.load(path2, suffix='_kernel'))
 
        filename = join(PATH.OUTPUT, 'action_hessian')
        solver.save(filename, solver.split(grad1-grad2))


    def setup(self):
        path = PATH.GLOBAL

        # prepare directory structure
        unix.rm(path)
        unix.mkdir(path)

        # set up workflow machinery
        preprocess.setup()
        postprocess.setup()

        system.run('solver', 'setup',
                   hosts='all')


    def evaluate_gradient(self, model, path):
        """ Performs forward simulation to evaluate objective function
        """
        unix.mkdir(path)
        solver.save(join(path, 'model'), solver.split(model))

        system.run('solver', 'eval_func',
                   hosts='all',
                   path=path)

        system.run('solver', 'eval_grad',
                   hosts='all',
                   path=path)

        postprocess.write_gradient(
            path=path)

