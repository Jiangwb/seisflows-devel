
import sys

from getpass import getuser
from os.path import abspath, exists, join
from uuid import uuid4
from seisflows.tools import unix
from seisflows.config import ParameterError,   custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class tigercpu_lg(custom_import('system', 'slurm_lg')):
    """ Specially designed system interface for tigercpu.princeton.edu

      See parent class SLURM_LG for more information
    """

    def check(self):
        """ Checks parameters and paths
        """

        if 'UUID' not in PAR:
            setattr(PAR, 'UUID', str(uuid4()))

        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', join('/scratch/gpfs', getuser(), 'seisflows', PAR.UUID))

        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', '')

        if 'NODESIZE' not in PAR:
            setattr(PAR, 'NODESIZE', 40)

        super(tigercpu_lg, self).check()


    def submit(self, *args, **kwargs):
        """ Submits job
        """
        if not exists(PATH.WORKDIR + '/' + 'scratch'):
            unix.ln(PATH.SCRATCH, PATH.WORKDIR + '/' + 'scratch')
        super(tigercpu_lg, self).submit(*args, **kwargs)


