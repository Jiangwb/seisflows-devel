
import os
import math
import sys
import time

from os.path import abspath, basename, exists, join
from subprocess import check_output
from uuid import uuid4
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class chinook_lg(custom_import('system', 'slurm_lg')):
    """ System interface for University of Alaska Fairbanks CHINOOK

      If you are using more than 48 cores per task, then add the following to
      your parameter file:
          SLURMARGS='--partition=t1standard'      

      For more informations, see 
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-interfaces
    """

    def check(self):
        """ Checks parameters and paths
        """
        # limit on number of concurrent tasks
        if 'NTASKMAX' not in PAR:
            setattr(PAR, 'NTASKMAX', 100)

        # number of cores per node
        if 'NODESIZE' not in PAR:
            setattr(PAR, 'NODESIZE', 24)

        # how to invoke executables
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', 'srun')

        # optional additional SLURM arguments
        if 'SLURMARGS' not in PAR:
            setattr(PAR, 'SLURMARGS', '--partition=t1small')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', join(os.getenv('CENTER1'), 'scratch', str(uuid4())))

        super(chinook_lg, self).check()


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)
        unix.mkdir(PATH.WORKDIR+'/'+'output.slurm')

        if not exists('./scratch'): 
            unix.ln(PATH.SCRATCH, PATH.WORKDIR+'/'+'scratch')

        workflow.checkpoint()

        # prepare sbatch arguments
        call('sbatch '
                + '%s ' % PAR.SLURMARGS
                + '--partition=%s ' % 't1small' # overloads SLURMARGS 
                + '--job-name=%s ' % PAR.TITLE
                + '--output %s ' % (PATH.WORKDIR+'/'+'output.log')
                + '--ntasks-per-node=%d ' % PAR.NODESIZE
                + '--nodes=%d ' % 1
                + '--time=%d ' % PAR.WALLTIME
                + findpath('seisflows.system') +'/'+ 'wrappers/submit '
                + PATH.OUTPUT)


    def mpiexec(self):
        """ Specifies MPI exectuable; used to invoke solver
        """
        return 'mpirun -np %d ' % PAR.NPROC

