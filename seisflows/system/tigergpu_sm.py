
import sys

from math import ceil
from os.path import abspath, join, exists
from uuid import uuid4
from seisflows.tools import unix
from seisflows.tools.tools import call, pkgpath
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class tigergpu_sm(custom_import('system', 'slurm_sm')):
    """ Specially designed system interface for tigergpu.princeton.edu

      See parent class for more information.
    """

    def check(self):
        """ Checks parameters and paths
        """
        if 'MPIEXEC' in PAR:
            print 'Ignoring user-supplied MPIEXEC parameter'

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', PATH.WORKDIR+'/'+'scratch')

        super(tigergpu_sm, self).check()


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)

        self.checkpoint()

        # submit workflow
        call('sbatch '
                + '%s ' %  PAR.SLURMARGS
                + '--job-name=%s '%PAR.TITLE
                + '--output=%s '%(PATH.WORKDIR +'/'+ 'output.log')
                + '--ntasks=%d '%PAR.NTASK
                + '--nodes=%d '%ceil(PAR.NTASK/4.)
                + '--ntasks-per-node=%d '%min(PAR.NTASK,4)
                + '--gres=gpu:%d '%min(PAR.NTASK,4)
                + '--time=%d '%PAR.WALLTIME
                + pkgpath('seisflows') +'/'+ 'system/wrappers/submit '
                + PATH.OUTPUT)


    def run(self, classname, method, hosts='all', **kwargs):
        """ Executes the following task:
              classname.method(*args, **kwargs)
        """
        self.checkpoint()
        self.save_kwargs(classname, method, kwargs)

        if hosts == 'all':
            # run on all available nodes
            call(join(pkgpath('seisflows-hpc'), 'system/wrappers/dsh_tigergpu') + ' '
                    + join(pkgpath('seisflows'), 'system/wrappers/run') + ' '
                    + PATH.OUTPUT + ' '
                    + classname + ' '
                    + method + ' '
                    + str(PAR.NTASK) + ' '
                    + PAR.ENVIRONS)

        elif hosts == 'head':
            # run on head node
            call('srun '
                    + '--ntasks=1 '
                    + '--nodes=1 '
                    + join(pkgpath('seisflows'), 'system/wrappers/run')
                    + PATH.OUTPUT + ' '
                    + classname + ' '
                    + method + ' '
                    + PAR.ENVIRONS)


    def mpiexec(self):
        """ Specifies MPI executable used to invoke solver
        """
        return 'mpirun -np %d --mca plm isolated --mca ras simulator ' % PAR.NPROC


