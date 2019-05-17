
from glob import glob
from os.path import basename, join

import sys
import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import cast, exists
from seisflows.config import ParameterError

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']



class calculate_weights(object):
    """ Calculates weights based on the proximity of one station to another

    The resulting geographic weights can be used in a "modified residual"
    inversion to balance uneven station distributions.
    (see seisflows-research/preprocess/modified_residual.py)

    Generally, the idea is to upweight areas of poor coverage (such as isolated 
    ocean island stations) and downweight areas of good coverage (such as dense 
    regional arrays).

    For added benefits, geographic weights can also be used to balance uneven
    event distributions.
    """

    def check(self):
        if 'COORDS' not in PATH:
            raise ParameterError

        if not exists(PATH.COORDS):
            raise ParameterError

        if not hasattr(PAR, 'UNITS'):
            setattr(PAR, 'UNITS', 'lonlat')


    def main(self):
        """ Calculates weights for a variety of different smoothing lengths
        """
        x, y = self.read_coords()

        ratios = []
        for L in self.lengths():
            weights = self.calculate_weights(x, y, L)
            ratios += [weights.max()/weights.min()]

            filename = 'weights-%04.1f' % L
            self.write(filename, 
                np.column_stack((x, y, weights)))

        self.write('ratios',
           np.column_stack((self.lengths(), ratios)))


    def calculate_weights(self, x, y, L):
        """ Calculates weights based on smoothed "station density"
        """
        n = x.size
        w = np.zeros(n)
        for i in range(n):
            D = self.dist(x[i], y[i], x, y)
            w[i] = sum(np.exp(-(D/L)**2.))**(-1.)
        w *= n/sum(w)
        return w


    def dist(self, x1, y1, x2, y2):
        """ Calculates distance on the sphere
        """
        if PAR.UNITS in ['lonlat']:
            dlat = np.radians(y2-y1)
            dlon = np.radians(x2-x1)
            a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(y1)) \
                * np.cos(np.radians(y2)) * np.sin(dlon/2) * np.sin(dlon/2)
            D = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            D *= 180/np.pi # radians to degrees
            return D
        else:
            return ((x1-x2)**2 + (y1-y2)**2)**0.5


    def read_coords(self):
        """ Reads station coordinates from text file
        """
        coords = np.loadtxt(PATH.COORDS)
        return coords[:,0], coords[:,1]


    def lengths(self):
        return np.linspace(0.5, 90., 180)


    def write(self, filename, array):
        fullfile = join(PATH.OUTPUT, filename)
        np.savetxt(fullfile, array)

