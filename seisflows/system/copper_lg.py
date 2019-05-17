
from os.path import abspath, basename, join

from seisflows.tools import unix
from seisflows.config import custom_import
from seisflows.config import ParameterError, 

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class copper_lg(custom_import('system', 'pbs_lg')):
    """ Specially designed system interface for copper

      By hiding environment details behind a python interface layer, these 
      classes provide a consistent command set across different computing
      environments.

      For more informations, see 
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-interfaces
    """

    def check(self):
        """ Checks parameters and paths
        """

        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('..')))

        if 'SUBTITLE' not in PAR:
            setattr(PAR, 'SUBTITLE', basename(abspath('.')))

        if 'NODESIZE' not in PAR:
            setattr(PAR, 'NODESIZE', 32)

        if 'PBS_ARGS' not in PAR:
            setattr(PAR, 'PBS_ARGS', '-A ERDCH38424KSC -q standard ')

        super(copper_lg, self).check()


    def mpiargs(self):
        return 'aprun -n %d' % 1


    def _launch(self, classname, method, hosts='all'):
        unix.mkdir(PATH.SYSTEM)

        nodes = math.ceil(PAR.NTASK/float(PAR.NODESIZE))
        cores = PAR.NTASK%PAR.NODESIZE
        hours = PAR.STEPTIME/60
        minutes = PAR.STEPTIME%60
        walltime = 'walltime=%02d:%02d:00 '%(hours, minutes)

        # submit job
        with open(PATH.SYSTEM+'/'+'job_id', 'w') as f:
            args = ('/opt/pbs/12.1.1.131502/bin/qsub '
                + PAR.PBS_ARGS + ' '
                + '-l select=%d:ncpus=%d:mpiprocs=%d ' (nodes,PAR.NODESIZE,cores)
                + '-l %s ' % walltime
                + '-J 0-%s ' % (PAR.NTASK-1)
                + '-N %s ' % PAR.TITLE
                + '-o %s ' % (PATH.SUBMIT+'/'+'output.pbs/' + '$PBS_ARRAYID')
                + '-r y '
                + '-j oe '
                + '-V '
                + self.launch_args(hosts)
                + PATH.OUTPUT + ' '
                + classname + ' '
                + method + ' '
                + findpath('seisflows'))

            # print(args)
            subprocess.call(args, shell=1, stdout=f)

        # print("made it here to job id")
        # retrieve job ids
        with open(PATH.SYSTEM+'/'+'job_id', 'r') as f:
            line = f.readline()
            job = line.split()[-1].strip()
        if hosts == 'all' and PAR.NTASK > 1:
            nn = range(PAR.NTASK)
            # take number[].sdb and replace with number[str(ii)]].sdb
            jobMain = job.split('[',1)[0]
            # print(jobMain)
            return [jobMain+'['+str(ii)+'].sdb' for ii in nn]
        else:
            return [job]



    def _query(self, jobid):
        """ Queries job state from PBS database
        """
        with open(PATH.SYSTEM+'/'+'job_status', 'w') as f:
            subprocess.call('/opt/pbs/12.1.1.131502/bin/qstat -x -tJ '  
                + jobid + ' | '
                + 'tail -n 1 ' + ' | '
                + 'awk \'{print $5}\'', 
                shell=True, 
                stdout=f)


        with open(PATH.SYSTEM+'/'+'job_status', 'r') as f:
            line = f.readline()
            state = line.strip()

        return state

