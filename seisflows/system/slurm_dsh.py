
import os
import re
import sys

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class slurm_dsh(custom_import('system', 'base')):
    """ An interface through which to WORKDIR workflows, run tasks in serial or 
      parallel, and perform other system functions.

      By hiding environment details behind a python interface layer, these 
      classes provide a consistent command set across different computing
      environments.

      Intermediate files are written to a global scratch path PATH.SCRATCH,
      which must be accessible to all compute nodes.

      Optionally, users can provide a local scratch path PATH.LOCAL if each
      compute node has its own local filesystem.

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

        # number of cores per node
        if 'NODESIZE' not in PAR:
            raise ParameterError(PAR, 'NODESIZE')

        # optional additional SLURM arguments
        if 'SLURMARGS' not in PAR:
            setattr(PAR, 'SLURMARGS', '')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where output files are written
        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', PATH.WORKDIR+'/'+'output')

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', PATH.WORKDIR+'/'+'scratch')

        # where system files are written
        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', PATH.SCRATCH+'/'+'system')

        # optional local scratch path
        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)


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
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks=%d '%PAR.NTASK
                + '--time=%d '%PAR.WALLTIME
                + findpath('seisflows.system') +'/'+ 'wrappers/submit '
                + PATH.OUTPUT)


    def run(self, classname, method, hosts='all', **kwargs):
        """ Executes the following task:
              classname.method(*args, **kwargs)
        """
        self.checkpoint()
        self.save_kwargs(classname, method, kwargs)

        if hosts == 'all':
            # run on all available nodes
            call(findpath('seisflows.system')  +'/'+'wrappers/dsh '
                    + ','.join(self.hostlist()) + ' '
                    + findpath('seisflows.system')  +'/'+'wrappers/run '
                    + PATH.OUTPUT + ' '
                    + classname + ' '
                    + method + ' ' 
                    + PAR.ENVIRONS)

        elif hosts == 'head':
            # run on head node
            call('ssh ' + self.hostlist()[0] + ' '
                    + '"'
                    + 'export SEISFLOWS_TASK_ID=0; '
                    + join(findpath('seisflows.system'), 'wrappers/run ')
                    + PATH.OUTPUT + ' '
                    + classname + ' '
                    + method + ' '
                    + PAR.ENVIRONS
                    +'"')

        else:
            raise(KeyError('Hosts parameter not set/recognized.'))


    def hostlist(self):
        """ Generates list of allocated cores
        """
        tasks_per_node = []
        for pattern in os.getenv('SLURM_TASKS_PER_NODE').split(','):
            match = re.search('([0-9]+)\(x([0-9]+)\)', pattern)
            if match:
                i,j = match.groups()
                tasks_per_node += [int(i)]*int(j)
            else:
                tasks_per_node += [int(pattern)]

        with open(PATH.SYSTEM+'/'+'job_nodelist', 'w') as f:
            call('scontrol show hostname $SLURM_JOB_NODEFILE', stdout=f)

        with open(PATH.SYSTEM+'/'+'job_nodelist', 'r') as f:
            nodes = f.read().splitlines() 

        nodelist = []
        for i,j in zip(nodes, tasks_per_node):
            nodelist += [i]*j
        return nodelist
        

    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        return int(os.getenv('SEISFLOWS_TASK_ID'))


    def mpiexec(self):
        """ Specifies MPI exectuable; used to invoke solver
        """
        return ''
        #return 'mpirun -np %d '%PAR.NPROC


    def save_kwargs(self, classname, method, kwargs):
        kwargspath = join(PATH.OUTPUT, 'kwargs')
        kwargsfile = join(kwargspath, classname+'_'+method+'.p')
        unix.mkdir(kwargspath)
        saveobj(kwargsfile, kwargs)


