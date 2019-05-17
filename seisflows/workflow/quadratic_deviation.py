
from glob import glob
from os.path import join
from numpy.linalg import norm

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


class quadratic_deviation(object):
    """ By how much does seismic misfit function differ from a quadratic form? 
      Provides an answer based on the size of the third derivatives.
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
            setattr(PATH, 'MODEL_INIT', PATH.MODEL)

        if 'MODEL_TRUE' not in PATH:
            setattr(PATH, 'MODEL_TRUE', PATH.MODEL)

        if 'EVAL_TRUE' not in PATH:
            setattr(PATH, 'EVAL_TRUE', join(PATH.GLOBAL, 'eval_true'))

        if 'EVAL_INIT' not in PATH:
            setattr(PATH, 'EVAL_INIT', join(PATH.GLOBAL, 'eval_init'))

        if 'PERT_POS' not in PATH:
            setattr(PATH, 'PERT_POS', join(PATH.GLOBAL, 'pert_pos'))

        if 'PERT_NEG' not in PATH:
            setattr(PATH, 'PERT_NEG', join(PATH.GLOBAL, 'pert_neg'))


    def main(self):
        self.setup()

        model_true = solver.merge(solver.load(PATH.MODEL_TRUE))
        model_init = solver.merge(solver.load(PATH.MODEL_INIT))
        model_pert = model_true - model_init

        print 'Computing gradient wrt model_true...'
        self.evaluate_gradient(model_init, PATH.EVAL_TRUE)

        print 'Computing gradient wrt model_init...'
        self.evaluate_gradient(model_true, PATH.EVAL_INIT)

        grad_true = self.load(PATH.EVAL_TRUE)
        grad_init = self.load(PATH.EVAL_INIT)

        for eps in np.logspace(-4,2,7):

            print ''
            print 'Using peturbation of the form eps*dm'
            print ' eps:', eps
            print ' |dm|:', max(abs(model_pert))
            print ''

            eps *= model_true.max()/model_pert.max()

            unix.rm(PATH.PERT_POS)
            unix.rm(PATH.PERT_NEG)
            unix.mkdir(PATH.PERT_POS)
            unix.mkdir(PATH.PERT_NEG)

            print 'Computing gradient wrt model_pert...'
            self.evaluate_gradient(model_true + eps*model_pert, PATH.PERT_POS)
            self.evaluate_gradient(model_true - eps*model_pert, PATH.PERT_NEG)

            pert_pos = self.load(PATH.PERT_POS)
            pert_neg = self.load(PATH.PERT_NEG)

            # compute measure of size of third derivatives
            thresh = 1.e-3
            mask = (model_pert > thresh)

            vd = (grad_init-grad_true)[mask]
            vn = vd - (pert_pos-pert_neg)[mask]/(2.*eps)

            print ''
            print 'num:', max(abs(vn))
            print 'den:', max(abs(vd))**2.
            print 'ratio 1: %.3e' % (norm(vn,1)/norm(vd,1)**2)
            print 'ratio 2: %.3e' % (norm(vn,2)/norm(vd,2)**2)
            print 'ratio M: %.3e' % (norm(vn,np.inf)/norm(vd,np.inf)**2)
            print ''

            #filename = join(PATH.OUTPUT, 'top')
            #np.save(filename+'.npy', vn)
            #solver.save(filename, solver.split(vn))

            #filename = join(PATH.OUTPUT, 'bot')
            #np.save(filename+'.npy', vd)
            #solver.save(filename, solver.split(vd))


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


    def load(self, path):
        grad = solver.load(path +'/'+ 'kernels/sum', suffix='_kernel')
        return solver.merge(grad)


