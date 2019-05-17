
import copy
import random
import sys
import numpy as np

from glob import glob
from os.path import basename
from obspy.core import Stream, Trace
from seisflows.tools import unix
from seisflows.tools.tools import Struct, exists
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']
system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']
optimize = sys.modules['seisflows_optimize']
preprocess = sys.modules['seisflows_preprocess']


class source_encoding(custom_import('workflow', 'inversion')):
    """ Source encoding subclass
    """
    def check(self):
        """ Checks parameters, paths, and dependencies
        """
        super(source_encoding, self).check()

        # check source encoding parameters
        if 'ENCODING' not in PAR:
            setattr(PAR, 'ENCODING', 1)

        if 'FAILRATE' not in PAR:
            setattr(PAR, 'FAILRATE', 0.)

        if 'SHIFT' not in PAR and PAR.ENCODING in [3,4]:
            raise Exception

        if 'NT_PADDED' not in PAR:
            if PAR.ENCODING in [3,4]:
                PAR.NT_PADDED = PAR.NT + (PAR.NSRC-1)*PAR.SHIFT
            else:
                PAR.NT_PADDED = PAR.NT

        assert PAR.NTASK == 1
        assert exists(PATH.DATA)


    def setup(self):
        """ Lays groundwork for inversion
        """
        super(source_encoding, self).setup()
        self.prepare_data()


    def initialize(self):
        """ Prepares for next model update iteration
        """
        ws, ts = self.prepare_sources()
        wr = self.prepare_receivers()

        stats = {}
        stats['wr'] = wr
        stats['ws'] = ws
        stats['ts'] = ts

        # combine observations into 'supergather'
        self.combine(stats, tag='obs')

        # update sources and receivers
        solver.write_sources(
            self.get_source_coords(),
            stats=stats,
            mapping=lambda _: range(PAR.NSRC))

        solver.write_receivers(
            self.get_receiver_coords())

        super(source_encoding, self).initialize()


    def prepare_sources(self):
        """ Generates source encoding factors
        """
        if PAR.ENCODING == 0:
            ts = np.zeros(PAR.NSRC)
            fs = np.ones(PAR.NSRC)

        elif PAR.ENCODING == 1:
            # binary weights
            ts = np.zeros(PAR.NSRC)
            fs = np.sign(np.random.randn(PAR.NSRC))

        elif PAR.ENCODING == 2:
            # Gaussian weights
            ts = np.zeros(PAR.NSRC)
            fs = np.random.randn(PAR.NSRC)

        elif PAR.ENCODING == 3:
            # "staggered" shifts
            ts = np.arange(0, PAR.NSRC)*PAR.SHIFT*PAR.DT
            random.shuffle(ts)
            fs = np.ones(PAR.NSRC)

        elif PAR.ENCODING == 4:
            # random shifts
            ts = ((PAR.NSRC - 1)*PAR.SHIFT*PAR.DT)*np.random.rand(PAR.NSRC)
            fs = np.ones(PAR.NSRC)

        # collect factors
        return fs, ts


    def prepare_receivers(self):
        """ Generates receiver factors
        """
        if optimize.iter == 1:
            # generate receiver factors
            if PAR.FAILRATE == 0:
                rs = np.ones((PAR.NREC, PAR.NSRC))
            else:
                rs = np.random.rand(PAR.NREC, PAR.NSRC)
                rs = (rs > PAR.FAILRATE).astype(int)
            np.savetxt(PATH.SCRATCH + '/' + 'rs', rs, '%3d')

        return np.loadtxt(PATH.SCRATCH + '/' + 'rs')


    def combine(self, stats, tag='obs'):
        """ Combines data from multiple sources
        """
        dirnames = self.dirnames
        filenames = self.filenames

        nt = PAR.NT_PADDED
        dt = PAR.DT
        nr = PAR.NREC

        for ii, filename in enumerate(filenames):
            # create object to hold summed data
            data_sum = Stream()
            for ir in range(nr):
                data_sum.append(Trace(
                    data=np.zeros(nt, dtype='float32'),
                    header=globals()[tag][dirnames[0]][filename][ir].stats))

            # linear combination over sources
            for jj, dirname in enumerate(dirnames):
                data = self.copy_data(dirname, filename)
                imin = int(stats['ts'][jj]/dt)
                imax = imin + nt
                for ir in range(nr):
                    data[ir].data *= stats['wr'][ir,jj]
                    data[ir].data *= stats['ws'][jj]
                    data_sum[ir].data[imin:imax] += data[ir].data[imin:imax]

            # save to disk
            fullname = solver.cwd +'/'+ 'traces/' + tag
            preprocess.writer(data_sum, fullname, filename)


    def copy_data(self, filename, dirname, tag='obs'):
        if tag not in globals():
            self.prepare_data(tag)

        return copy.deepcopy(
            globals()[tag][filename][dirname])


    def prepare_data(self, tag='obs'):
        """ Loads data into memory
        """
        data = {}
        for dirname in self.dirnames:
            data[dirname] = {}
            fullpath = PATH.DATA +'/'+ dirname
            for filename in self.filenames:
                data[dirname][filename] = preprocess.reader(fullpath, filename)
        globals()[tag] = data


    def get_source_coords(self):
        sx = []
        sy = []
        sz = []
        for ii in range(PAR.NSRC):
            coords = preprocess.get_source_coords(
                globals()['obs'][self.dirnames[ii]][self.filenames[0]])
            sx += [coords[0][0]]
            sy += [coords[1][0]]
            sz += [coords[2][0]]
        return sx, sy, sz


    def get_receiver_coords(self):
        return preprocess.get_receiver_coords(
            globals()['obs'][self.dirnames[0]][self.filenames[0]])


    @property
    def dirnames(self):
            path = PATH.SPECFEM_DATA
            wildcard = solver.source_prefix+'_*'
            globstar = sorted(glob(path +'/'+ wildcard))
            if not globstar:
                 print msg.SourceError_SPECFEM % (path, wildcard)
                 sys.exit(-1)
            names = []
            for path in globstar:
                names += [basename(path).split('_')[-1]]
            return names


    @property
    def filenames(self):
        return solver.data_filenames



def cdiff_adjoint(wsyn, wobs, nt, dt):
    # cross correlation difference
    cdiff = _np.correlate(wobs,wsyn) - _np.correlate(wobs,wobs)
    wadj = _np.convolve(wobs,cdiff)
    return 1e-10 * wadj


def cdiff_misfit(wsyn, wobs, nt, dt):
    cdiff = np.correlate(wobs, wsyn) - np.correlate(wobs, wobs)
    return np.sqrt(np.sum(cdiff*cdiff*dt))

