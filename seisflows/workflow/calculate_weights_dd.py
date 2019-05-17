
from glob import glob
from os.path import basename, join

import sys
import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import cast, exists
from seisflows.config import ParameterError

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']



class calculate_weights_dd(object):
    """ Writes distances, counts and weights used in double difference inversion
    """

    def check(self):
        if 'COORDS' not in PATH:
            raise ParameterError

        if not exists(PATH.COORDS):
            raise ParameterError


    def main(self):

        x, y = self.read_coords()

        # calculate distances between stations
        dist = self.calculate_dist(x, y)

        # count station pairs
        count = self.count_pairs(dist)

        # calculate geographic weights
        ratios = []
        for L in self.lengths():
            weights = self.calculate_weights(x, y, L)
            ratios += [weights.max()/weights.min()]


    def read_coords(self):
        """ Reads station coordinates from text file
        """
        coords = np.loadtxt(PATH.COORDS)
        return coords[:,0], coords[:,1]


    def calculate_weights(self, x, y, L):
        """ Smooths discrete station distribution to obtain continuous 
          "station density"
        """
        n = x.size
        w = np.zeros(n)
        for i in range(n):
            D = self.distance(x[i], y[i], x, y)
            w[i] = sum(np.exp(-(D/L)**2.))**(-1.)
        w *= n/sum(w)
        return w


    def distance(self, lat1, lon1, lat2, lon2):
      """ Calculates distance on the sphere
      """
      dlat = np.radians(lat2-lat1)
      dlon = np.radians(lon2-lon1)
      a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) \
          * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
      D = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

      # radians to degrees
      D *= 180/np.pi

      return D


    def lengths(self):
        return np.linspace(0.5, 90. 180)


    def write(self, filename, array):
        """ Writes weights to text file
        """
        fullfile = join(PATH.OUTPUT, filename)
        np.savetxt(fullfile, array)

