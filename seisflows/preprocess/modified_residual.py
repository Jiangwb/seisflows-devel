
import sys
import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import Struct, exists
from seisflows.config import ParameterError, custom_import

from seisflows.plugins import adjoint, misfit, readers, writers

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']


class modified_residual(custom_import('preprocess', 'base')):
    """ Allows weighted inversion

     By modifying residuals and adjoint traces, weights the objective function 
     function differently; can be useful for balancing lopsided station or
     event distributions, among other things
    """

    def check(self):
        """ Checks parameters and paths
        """
        super(modified_residual, self).check()

        if 'RECEIVER_WEIGHTS' not in PATH:
            setattr(PATH, 'RECEIVER_WEIGHTS', None)

        if 'SOURCE_WEIGHTS' not in PATH:
            setattr(PATH, 'SOURCE_WEIGHTS', None)


        # assertions
        if PATH.RECEIVER_WEIGHTS:
            assert exists(PATH.RECEIVER_WEIGHTS)

        if PATH.SOURCE_WEIGHTS:
            assert exists(PATH.SOURCE_WEIGHTS)

        assert 'NREC' in PAR
        assert 'NSRC' in PAR



    def write_residuals(self, path, syn, dat):
        nt, dt, _ = self.get_time_scheme(syn)
        nn, _ = self.get_network_size(syn)

        rsd = np.zeros(nn)
        for ii in range(nn):
            rsd[ii] = self.misfit(syn[ii].data, dat[ii].data, nt, dt)

        # apply weights
        wr = self.receiver_weights()
        ws = self.source_weights()

        rsd *= wr
        rsd[ii] *= ws

        filename = path+'/'+'residuals'
        if exists(filename):
            rsd.extend(list(np.loadtxt(filename)))

        np.savetxt(filename, rsd)


    def write_adjoint_traces(self, path, syn, dat, channel):
        nt, dt, _ = self.get_time_scheme(syn)
        nn, _ = self.get_network_size(syn)

        wr = self.receiver_weights()
        ws = self.source_weights()

        adj = syn
        for ii in range(nn):
            adj[ii].data = self.adjoint(syn[ii].data, dat[ii].data, nt, dt)

            # apply weights
            adj[ii].data *= wr[ii]
            adj[ii].data *= ws

        self.writer(adj, path, channel)


    def receiver_weights(self):
        if PATH.RECEIVER_WEIGHTS:
            return np.loadtxt(PATH.RECEIVER_WEIGHTS)[:,-1]
        else:
            return np.ones(PAR.NREC)


    def source_weights(self):
        if PATH.SOURCE_WEIGHTS:
            return np.loadtxt(PATH.SOURCE_WEIGHTS)[system.taskid(),-1]
        else:
            return 1.

