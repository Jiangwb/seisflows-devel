
from os.path import exists
from uuid import uuid4

import os
import sys

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class chinook_sm(custom_import('system', 'slurm_sm')):
    """ System interface for University of Alaska Fairbanks CHINOOK

      For important additional information, please see 
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-configuration
    """


    def check(self):
        """ Checks parameters and paths
        """
        # name of job
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # time allocated for workflow in minutes
        if 'WALLTIME' not in PAR:
            setattr(PAR, 'WALLTIME', 30.)
         
        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')
    
        # how to invoke executables
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', '') 
    
        # optional additional SLURM arguments
        if 'SLURMARGS' not in PAR:
            setattr(PAR, 'SLURMARGS', '')

        # SLURM resource partition
        if 'PARTITION' not in PAR:
            setattr(PAR, 'PARTITION', 't1small')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', join(os.getenv('CENTER1'), 'scratch', str(uuid4())))

        # where output files are written
        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', PATH.WORKDIR+'/'+'output')

        # where system files are written
        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', PATH.SCRATCH+'/'+'system')

        # optional local scratch path
        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)


    def submit(self, workflow):
        """ Submits workflow
        """
        unix.cd(PATH.WORKDIR)
        if not exists('./scratch'): 
            unix.ln(PATH.SCRATCH, PATH.WORKDIR+'/'+'scratch')

        unix.mkdir(PATH.OUTPUT)
        workflow.checkpoint()

        # prepare sbatch arguments
        call('sbatch '
                + '%s ' % PAR.SLURMARGS
                + '--partition=%s ' % PAR.PARTITION
                + '--job-name=%s ' % PAR.TITLE
                + '--output %s ' % (PATH.WORKDIR+'/'+'output.log')
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks=%d '%PAR.NTASK
                + '--time=%d ' % PAR.WALLTIME
                + findpath('seisflows.system') +'/'+ 'wrappers/submit '
                + PATH.OUTPUT)

