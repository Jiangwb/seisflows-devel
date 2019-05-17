
from glob import glob

import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.array import  mesh2grid, grid2mesh, stack
from seisflows.tools.tools import call, exists
from seisflows.config import , \
    ParameterError, custom_import
from seisflows.tools.math import grad, nabla, nabla2

from seisflows.plugins.io import sem

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']
optimize = sys.modules['seisflows_optimize']


class mumford_shah(custom_import('postprocess', 'regularize')):

    def check(self):
        """ Checks parameters and paths
        """
        super(mumford_shah, self).check()

        # check parameters
        if 'FIXRADIUS' not in PAR:
            setattr(PAR, 'FIXRADIUS', 7.5)

        if 'GAMMA' not in PAR:
            setattr(PAR, 'GAMMA', 0.)

        if 'ETA' not in PAR:
            setattr(PAR, 'ETA', 0.)

        if 'SMOOTH_EDGES' not in PAR:
            setattr(PAR, 'SMOOTH_EDGES', 5.)

        # check paths
        if 'MUMFORD_SHAH_INPUT' not in PATH:
            raise ParameterError

        if 'MUMFORD_SHAH_OUTPUT' not in PATH:
            raise ParameterError

        if 'MUMFORD_SHAH_CONFIG' not in PATH:
            raise ParameterError

        if 'MUMFORD_SHAH_BIN' not in PATH:
            raise ParameterError

        assert PAR.GAMMA >= 0
        assert PAR.ETA >= 0 


    def write_gradient(self, path):
        super(mumford_shah, self).write_gradient(path)

        g = solver.load(path +'/'+ 'gradient', suffix='_kernel')
        m = solver.load(path +'/'+ 'model')
        mesh = self.getmesh()

        for parameter in solver.parameters:
            for iproc in range(PAR.NPROC):
                g[parameter][iproc] += PAR.GAMMA *\
                    sem.read(PATH.MUMFORD_SHAH_OUTPUT, parameter+'_dm', iproc)

        # save gradient
        self.save(path, solver.merge(g), backup='noregularize')

        # save edges
        src = PATH.MUMFORD_SHAH_OUTPUT
        dst = PATH.OUTPUT+'/'+'mumford_shah'+('_%04d' % optimize.iter)
        unix.mv(src, dst)


    def detect_edges(self):
        path_input = PATH.MUMFORD_SHAH_INPUT
        path_output = PATH.MUMFORD_SHAH_OUTPUT
        path_run = PATH.SUBMIT

        unix.cp(glob(PATH.GRAD+'/'+'model/*'), path_input)
        unix.mkdir(path_output)
        unix.cd(path_run)

        # writes damping term to disk
        with open('mumford_shah.log', 'w') as fileobj:
            call('srun -n 1 -N 1 ' +PATH.MUMFORD_SHAH_BIN+'/'+'psemimage ' +
                 PATH.MUMFORD_SHAH_CONFIG +
                 ' -ksp_type fgmres ' +
                 ' -pc_type asm ' +
                 ' -ksp_gmres_restart 300 ',
                 shell=True,
                 stdout=fileobj)

        for parameter in solver.parameters:
            self.apply_smoothing(parameter)
            self.write_damping_term(parameter)


    def apply_smoothing(self, parameter):
        from seisflows.tools.array import meshsmooth, stack

        coords = []
        for key in ['x', 'z']:
            coords += [sem.read(PATH.MODEL_INIT, key, 0)]
        mesh = stack(*coords)
        
        for suffix in ['_nu']:
            path = PATH.MUMFORD_SHAH_OUTPUT

            if PAR.SMOOTH_EDGES > 0.:
                # backup original
                kernel = sem.read(path, parameter+suffix, 0)
                sem.write(kernel, path, parameter+suffix+'_nosmooth', 0)

                # apply smoothing operator
                kernel = meshsmooth(kernel, mesh, PAR.SMOOTH_EDGES)
                sem.write(kernel, path, parameter+suffix, 0)


    def write_damping_term(self, parameter):
        path_coords = PATH.OUTPUT+'/'+'model_init'
        path_input = PATH.GRAD+'/'+'model'
        path_output = PATH.MUMFORD_SHAH_OUTPUT
        path_run = PATH.SUBMIT

        x = sem.read(path_coords, 'x', 0)
        z = sem.read(path_coords, 'z', 0)
        mesh = stack(x,z)

        m, grid = mesh2grid(sem.read(path_input, parameter, 0), mesh)
        nu, _ = mesh2grid(sem.read(path_output, parameter+'_nu', 0), mesh)

        grad_m = grad(m)
        grad_nu = grad(nu)

        V = -2.*(grad_m[0]*grad_nu[0] + grad_m[1]*grad_nu[1]) +\
            -nu**2 * nabla2(m)

        v = grid2mesh(V, grid, mesh)

        sem.write(v, path_output, parameter+'_dm', 0)


    def process_kernels(self, path, parameters):
        """ Processes kernels in accordance with parameter settings
        """
        fullpath = path +'/'+ 'kernels'
        assert exists(path)

        if exists(fullpath +'/'+ 'sum'):
            unix.mv(fullpath +'/'+ 'sum', fullpath +'/'+ 'sum_nofix')

        system.run('postprocess', 'fix_near_field', 
                   hosts='all', 
                   path=fullpath)

        system.run('solver', 'combine',
                   hosts='head',
                   path=fullpath,
                   parameters=parameters)

        self.detect_edges()



