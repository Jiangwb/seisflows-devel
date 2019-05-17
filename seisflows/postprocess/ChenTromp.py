
import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.tools import exists
from seisflows.config import , \
    ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']


class ChenTromp(custom_import('postprocess', 'base')):
    """ Postprocessing class
    """

    def write_gradient(self, path):
        """ Writes gradient of objective function
        """
        # check parameters
        if 'OPTIMIZE' not in PATH:
            raise ParameterError(PATH, 'OPTIMIZE')

        # check input arguments
        if not exists(path):
            raise Exception()

        self.combine_kernels(path)
        self.process_kernels(path)

        g = solver.merge(solver.load(
                path +'/'+ 'kernels/sum',
                suffix='_kernel',
                verbose=True))

        # apply scaling
        if float(PAR.SCALE) == 1.:
            pass
        elif not PAR.SCALE:
            pass
        else:
            g *= PAR.SCALE

        # write gradient
        solver.save(PATH.GRAD +'/'+ 'gradient', solver.split(g), suffix='_kernel')
        savenpy(PATH.OPTIMIZE +'/'+ 'g_new', g)


        try:
            for iproc in range(PAR.NPROC):
                y = g['Gs'][iproc]
                x = - g['Gc'][iproc]
                t = 0.5*np.arctan2(y, x)
                filename = 'proc%06d_%s.bin' % (iproc, 'azimuth')
                savebin(t, PATH.GRAD +'/'+ filename)
        except:
            pass

