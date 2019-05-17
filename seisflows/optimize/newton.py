
import sys
import numpy as np

from seisflows.tools import unix
from seisflows.config import ParameterError, custom_import
from seisflows.plugins import optimize

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


#print " WARNING: Truncated Newton routines were extensively refactored, and the new version has not been thoroughly tested"



class newton(custom_import('optimize', 'base')):
    """ Implements Newton-CG algorithm
    """

    def check(self):
        """ Checks parameters and paths
        """
        # line search method
        if 'LINESEARCH' not in PAR:
            setattr(PAR, 'LINESEARCH', 'Backtrack')

        # LCG preconditioner
        if 'LCGPRECOND' not in PAR:
            setattr(PAR, 'LCGPRECOND', None)

        # Eisenstat-Walker stopping condition
        if 'LCGFORCE' not in PAR:
            setattr(PAR, 'LCGFORCE', 1.)

        # maximum number of LCG iterations
        if 'LCGMAX' not in PAR:
            setattr(PAR, 'LCGMAX', 2)

        # LCG restart threshold
        if 'LCGTHRESH' not in PAR:
            setattr(PAR, 'LCGTHRESH', np.inf)

        # finite difference pertubation
        if 'EPSILON' not in PAR:
            setattr(PAR, 'EPSILON', 1.)

        super(newton, self).check()


    def setup(self):
        super(newton, self).setup()

        # prepare algorithm machinery
        self.LCG = getattr(optimize, 'PLCG')(
            path=PATH.OPTIMIZE, 
            thresh=PAR.LCGTHRESH, 
            maxiter=PAR.LCGMAX, 
            precond=PAR.LCGPRECOND,
            eta=PAR.LCGFORCE)


    def compute_direction(self):
        self.restarted = False

        m = self.load('m_new')
        g = self.load('g_new')

        self.LCG.initialize()

        # loop over LCG iterations
        for self.ilcg in range(1, PAR.LCGMAX+1):
            if PAR.VERBOSE:
                print " LCG iteration", self.ilcg

            dm = self.load('LCG/p')

            # finite difference pertubation
            h = PAR.EPSILON/max(abs(dm))

            # compute Hessian-vector product by finite differences
            Hdm = self.apply_hessian(m, dm, h)

            # perform LCG iteration
            status = self.LCG.update(Hdm)

            if status > 0:
                # finalize model update
                dm = self.load('LCG/x')
                if self.dot(g,dm) >= 0:
                    print ' Newton direction rejected [not descent direction]'
                    dm = -g
                    self.restarted = True
                self.save('p_new', dm)
                break


    def apply_hessian(self, m, dm, h):
        """ Computes the action of the Hessian on a given vector through
          solver calls
        """
        system = sys.modules['seisflows_system']
        solver = sys.modules['seisflows_solver']
        postprocess = sys.modules['seisflows_postprocess']

        self.save('m_lcg', m + h*dm)

        solver.save(solver.split(m + h*dm), 
                PATH.HESS+'/'+'model')

        system.run('optimize', 'apply_hess',
                path=PATH.HESS)

        postprocess.write_gradient(
                path=PATH.HESS)

        self.save('g_lcg', solver.merge(solver.load(
                PATH.HESS+'/'+'gradient', suffix='_kernel')))

        # uncomment for debugging
        #if True:
        #    unix.rm(PATH.HESS+'_debug')
        #    unix.mv(PATH.HESS, PATH.HESS+'_debug')
        #    unix.mkdir(PATH.HESS)

        unix.rm(PATH.HESS)
        unix.mkdir(PATH.HESS)

        return self.hessian_product(h)


    def hessian_product(self, h):
        # for Gauss-Newton model updates simply overload this method
        return (self.load('g_lcg') - self.load('g_new'))/h


    def restart(self):
        # not required for this subclass since restarts are handled by 
        # compute_direction
        pass


    def apply_hess(self, path=''):
        """ Computes action of Hessian on a given model vector.
        """
        solver = sys.modules['seisflows_solver']

        unix.cd(solver.cwd)
        solver.import_model(path)
        unix.mkdir('traces/lcg')
        solver.forward('traces/lcg')
        self.prepare_apply_hess(solver.cwd)
        solver.adjoint()
        solver.export_kernels(path)


    def prepare_apply_hess(self, path='.'):
        """ Prepares solver to compute action of Hessian by writing adjoint traces
        """
        solver = sys.modules['seisflows_solver']
        preprocess = sys.modules['seisflows_preprocess']

        tag1, tag2 = self.apply_hess_tags()

        for filename in solver.data_filenames:
            dat1 = preprocess.reader(path+'/'+'traces/'+tag1, filename)
            dat2 = preprocess.reader(path+'/'+'traces/'+tag2, filename)

            dat1 = preprocess.apply_filter(dat1)
            dat1 = preprocess.apply_mute(dat1)
            dat1 = preprocess.apply_normalize(dat1)

            dat2 = preprocess.apply_filter(dat2)
            dat2 = preprocess.apply_mute(dat2)
            dat2 = preprocess.apply_normalize(dat2)

            preprocess.write_adjoint_traces(path+'/'+'traces/adj', dat1, dat2, filename)


    def apply_hess_tags(self):
        if PAR.OPTIMIZE in ['newton']:
           tag1, tag2 = 'lcg', 'obs'
        elif PAR.OPTIMIZE in ['gauss_newton']:
           tag1, tag2 = 'lcg', 'syn'
        else:
           tag1, tag2 = 'lcg', 'obs'
        return tag1, tag2

