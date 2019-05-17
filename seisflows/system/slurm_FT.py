
import os
import math
import sys
import time

from os.path import abspath, basename, join
from seisflows.tools import msg
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj, timestamp
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class slurm_FT(custom_import('system', 'slurm_lg')):
    """ Adds fault tolerance to slurm_lg
    """

    def check(self):
        """ Checks parameters and paths
        """
        super(slurm_FT, self).check()


    def resubmit_failed_job(self, classname, method, jobs, taskid):
        with open(PATH.SYSTEM+'/'+'job_id', 'w') as file:
            call(self.resubmit_cmd(classname, method, taskid),
                stdout=file)

        with open(PATH.SYSTEM+'/'+'job_id', 'r') as file:
            line = file.readline()
            jobid = line.split()[-1].strip()

        # remove failed job from list
        jobs.pop(taskid)

        # add resubmitted job to list
        jobs.insert(taskid, jobid)
        return jobs


    def resubmit_cmd(self, classname, method, taskid):
        return ('sbatch '
                + '%s ' % PAR.SLURMARGS
                + '--job-name=%s ' % PAR.TITLE
                + '--nodes=%d ' % math.ceil(PAR.NPROC/float(PAR.NODESIZE))
                + '--ntasks-per-node=%d ' % PAR.NODESIZE
                + '--ntasks=%d ' % PAR.NPROC
                + '--time=%d ' % PAR.TASKTIME
                + '--output=%s ' % (PATH.WORKDIR+'/'+'output.slurm/'+'%j')
                + '--export=TASKID=%d ' % taskid
                + findpath('seisflows.system') +'/'+ 'wrappers/run '
                + PATH.OUTPUT + ' '
                + classname + ' '
                + method + ' ' 
                + PAR.ENVIRONS)


    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        if os.getenv('SLURM_ARRAY_TASK_ID'):
            return int(os.getenv('SLURM_ARRAY_TASK_ID'))
        else:
            try:
                return int(os.getenv('TASKID'))
            except:
                raise Exception("TASKID environment variable not defined.")


    def job_array_status(self, classname, method, jobs):
        """ Determines completion status of one or more jobs
        """
        states = []
        for taskid, job in enumerate(jobs):
            state = self._query(job)
            if state in ['TIMEOUT']:
                print msg.TimoutError % (classname, method, job, PAR.TASKTIME)
                sys.exit(-1)
            elif state in ['FAILED', 'NODE_FAIL']:
                print ' task %d failed, retrying' % taskid
                jobs = self.resubmit_failed_job(classname, method, jobs, taskid)
                states += [0]

            elif state in ['COMPLETED']:
                states += [1]
            else:
                states += [0]

        isdone = all(states)

        return isdone, jobs


