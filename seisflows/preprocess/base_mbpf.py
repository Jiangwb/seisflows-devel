
import sys
import numpy as np
import obspy

from seisflows.tools import msg, unix
from seisflows.tools.tools import exists, getset

from seisflows.plugins import adjoint, misfit, readers, writers
from seisflows.tools import signal
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class base_mbpf(custom_import('preprocess','base')):
    """ multi-bandpass filter strategy data preprocessing class

      Provides data processing functions for multi-bandpass filter strategy
    """

    def check(self):
        """ Checks parameters and paths
        """
        # used for inversion
        if 'BANDPASS_GROUP' not in PAR:
            raise ParameterError(PAR, 'BANDPASS_GROUP')


    def prepare_eval_grad(self, path='.'):
        """
         Prepares solver for gradient evaluation by writing residuals and
         adjoint traces

         :input path: directory containing observed and synthetic seismic data
        """
        solver = sys.modules['seisflows_solver']

        for igroup in range(PAR.BANDPASS_GROUP):
            if igroup==0:
                freq_min = PAR.FREQMIN0 
                freq_max = PAR.FREQMAX0
                unix.mkdir(path+'/'+'traces/adj0')
            if igroup==1:
                freq_min = PAR.FREQMIN1 
                freq_max = PAR.FREQMAX1 
                unix.mkdir(path+'/'+'traces/adj1')
            if igroup==2:
                freq_min = PAR.FREQMIN2 
                freq_max = PAR.FREQMAX2 
                unix.mkdir(path+'/'+'traces/adj2')
            if igroup==3:
                freq_min = PAR.FREQMIN3 
                freq_max = PAR.FREQMAX3 
                unix.mkdir(path+'/'+'traces/adj3')
            if igroup==4:
                freq_min = PAR.FREQMIN4 
                freq_max = PAR.FREQMAX4
                unix.mkdir(path+'/'+'traces/adj4')
            print 'igroup='
            print(igroup)
            for filename in solver.data_filenames:
                obs = self.reader(path+'/'+'traces/obs', filename)
                syn = self.reader(path+'/'+'traces/syn', filename)

                # process observations
                obs = self.apply_filter(obs, freq_min, freq_max)
                obs = self.apply_mute(obs)
                obs = self.apply_normalize(obs)

                # process synthetics
                syn = self.apply_filter(syn, freq_min, freq_max)
                syn = self.apply_mute(syn)
                syn = self.apply_normalize(syn)

                if PAR.MISFIT:
                    self.write_residuals(path, syn, obs)

                self.write_adjoint_traces(path+'/'+'traces/adj'+'%d'%igroup, syn, obs, filename)
                ## calculate adjoint source here
                #nt, dt, _ = self.get_time_scheme(syn)
                #nr, _ = self.get_network_size(syn)
                ##adj = syn
                #for ii in range(nr):
                #    adj[igroup,ii].data = self.adjoint(syn[ii].data, obs[ii].data, nt, dt)

        adj_sum = syn
        nr, _ = self.get_network_size(syn)
        for ir in range(nr):
            adj_sum[ir].data[:] = 0.0
			
        for igroup in range(PAR.BANDPASS_GROUP):
            #print 'SUMMATION, igroup='
            #print(igroup)
            for filename in solver.data_filenames:
            #for filename in self.adj_filenames:
                adj = self.reader(path+'/'+'traces/adj'+'%d'%igroup, filename)
                for ir in range(nr):
                    adj_sum[ir].data = adj_sum[ir].data + adj[ir].data

        # output adj_sum
        for filename in solver.data_filenames:
            self.writer(adj_sum, path+'/'+'traces/adj', filename)


    def adj_filenames(self):
        if PAR.CHANNELS:
            if PAR.FORMAT in ['SU', 'su']:
               filenames = []
               for channel in PAR.CHANNELS:
                   filenames += ['U%s_file_single.su.adj' % channel]
               return filenames

        else:
            unix.cd(self.cwd)
            unix.cd('traces/obs')

            if PAR.FORMAT in ['SU', 'su']:
                return glob('U?_file_single.su.adj')


    def apply_filter(self, traces, freq_min, freq_max):
        if not PAR.FILTER:
            return traces

        elif PAR.FILTER == 'Bandpass':
            for tr in traces:
                tr.detrend('demean')
                tr.detrend('linear')
                tr.taper(0.05, type='hann')
                tr.filter('bandpass',
                          zerophase=True,
                          freqmin=freq_min,
                          freqmax=freq_max)
        else:
            raise ParameterError()

        return traces


