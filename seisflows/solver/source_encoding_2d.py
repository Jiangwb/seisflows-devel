
import sys
import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import exists
from seisflows.config import ParameterError, custom_import

import seisflows.plugins.solver.specfem2d as solvertools

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']
system = sys.modules['seisflows_system']
preprocess = sys.modules['seisflows_preprocess']


class source_encoding_2d(custom_import('solver', 'specfem2d')):
    def check(self):
        """ Checks parameters, paths, and dependencies
        """
        super(source_encoding_2d, self).check()


    def initialize_solver_directories(self):
        """ Sets up directory in which to run solver
        """
        if 'NT_PADDED' not in PAR:
            raise Exception

        super(source_encoding_2d, self).initialize_solver_directories()
        solvertools.setpar('NSOURCES', PAR.NSRC)
        solvertools.setpar('nt', PAR.NT_PADDED)


    def write_receivers(self, coords):
        """ Writes receivers file
        """
        solvertools.write_receivers(
            coords,
            self.cwd)


    def write_sources(self, coords, stats=[], mapping=lambda i: [i]):
        """ Writes sources file
        """
        unix.cd(self.cwd)
        nodes = mapping(system.taskid())
        lines = []
        for i in nodes:
            solvertools.write_sources(
                [coords[0][i], coords[1][i], coords[2][i]],
                self.cwd,
                stats['ws'][i])

            with open('DATA/SOURCE', 'r') as f:
                lines.extend(f.readlines())

        with open('DATA/SOURCE', 'w') as f:
            f.writelines(lines)

