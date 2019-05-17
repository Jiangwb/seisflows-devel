
from getpass import getuser
from os.path import abspath, basename, join

from seisflows.config import ParameterError, , custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class icex_lg(custom_import('system', 'lsf_lg')):
    """ Specially designed system interface for ICEXDEV

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

        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH',
                    join('/scratch/gpfs', getuser(), PAR.TITLE, PAR.SUBTITLE))

        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', '')

        if 'NODESIZE' not in PAR:
            setattr(PAR, 'NODESIZE', 16)

        if 'LSF_ARGS' not in PAR:
            setattr(PAR, 'LSF_ARGS', '-a intelmpi -q LAURE_USERS')

        super(icex_lg, self).check()


    def mpiargs(self):
        #return 'mpirun '
        #return ('/apps/lsf/cluster_ICEX/8.3/linux2.6-glibc2.3-x86_64/bin/mpirun.lsf '
        #        + '-genv I_MPI_EXTRA_FILESYSTEM 1 -genv I_MPI_EXTRA_FILESYSTEM_LIST lustre '
        #        + '-genv I_MPI_PIN 0 -genv I_MPI_FALLBACK 0 -_MSG_SIZE 4194304 -pam ')
        return ('/apps/lsf/cluster_ICEX/8.3/linux2.6-glibc2.3-x86_64/bin/mpirun.lsf '
                + '-genv I_MPI_EXTRA_FILESYSTEM 1 -genv I_MPI_EXTRA_FILESYSTEM_LIST lustre '
                + '-genv I_MPI_PIN 0 -genv I_MPI_FALLBACK 0 -genv I_MPI_RDMA_RNDV_WRITE 1 -genv I_MPI_RDMA_MAX_MSG_SIZE 4194304 -pam '
                + ' "-n %s " ' % PAR.NPROC )


