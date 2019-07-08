
import sys

from os.path import join

from seisflows.plugins.io import sem
from seisflows.tools.shared import Minmax
from seisflows.tools.shared import Model as IOStruct

from seisflows.tools import unix
from seisflows.tools.tools import exists
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

#######original#######
#class elastic(object):
#######original#######
#######Jiang change start#######
class elastic(custom_import('solver','specfem2d')):
#######Jiang change end#######
    """ Adds elastic inversion machinery
    """
    if PAR.MATERIALS == 'phi_beta':
        from seisflows.plugins.materials import phi_beta_forward as map_forward
        from seisflows.plugins.materials import phi_beta_inverse as map_inverse
        model_parameters = []
        model_parameters += ['vp']
        model_parameters += ['vs']
        kernel_parameters = []
        kernel_parameters += ['bulk_c']
        kernel_parameters += ['bulk_beta']

    elif PAR.MATERIALS == 'kappa_mu':
        from seisflows.plugins.materials import kappa_mu_forward as map_forward
        from seisflows.plugins.materials import kappa_mu_inverse as map_inverse
        model_parameters = []
        model_parameters += ['vp']
        model_parameters += ['vs']
        kernel_parameters = []
        kernel_parameters += ['kappa']
        kernel_parameters += ['mu']
        parameters = []
        parameters += ['kappa']
        parameters += ['mu']

    elif PAR.MATERIALS == 'lambda_mu':
        from seisflows.plugins.materials import lambda_mu_forward as map_forward
        from seisflows.plugins.materials import lambda_mu_inverse as map_inverse
        model_parameters = []
        model_parameters += ['vp']
        model_parameters += ['vs']
        kernel_parameters = []
        kernel_parameters += ['lame1']
        kernel_parameters += ['lame2']

    elif PAR.MATERIALS == 'alpha_beta':
        from seisflows.plugins.materials import vp_vs_forward as map_forward
        from seisflows.plugins.materials import vp_vs_inverse as map_inverse
        model_parameters = []
        model_parameters += ['vp']
        model_parameters += ['vs']
        kernel_parameters = []
        kernel_parameters += ['vp']
        kernel_parameters += ['vs']


    if PAR.DENSITY == 'Variable':
        density_scaling = None
        model_parameters += ['rho']
        kernel_parameters += ['rho']
    elif PAR.DENSITY == 'Constant':
        density_scaling = None
    elif PAR.DENSITY == 'Gardner':
        from seisflows.plugins.materials import rho_gardner as density_scaling


#######original#######
#    def load(self, path, prefix='', suffix='', verbose=True):
#######original#######
#######Jiang change start#######
    def load(self, path, parameters=[], prefix='', suffix='', verbose=True):
#######Jiang change end#######
        """ reads SPECFEM model or kernels
        """
        logpath = PATH.SUBMIT

        if 'kernel' in suffix:
            kernels = IOStruct(self.kernel_parameters)

            minmax = Minmax(self.kernel_parameters)
            for iproc in range(self.mesh_properties.nproc):
                # read database files
                keys, vals = sem.mread(path, self.kernel_parameters, iproc, prefix, suffix)
                minmax.update(keys, vals)

                # store kernels
                for key, val in zip(keys, vals):
                    kernels[key] += [val]

            if verbose:
                minmax.write(path, logpath)
            return kernels

        else:
            model = IOStruct(self.kernel_parameters)

            minmax = Minmax(self.model_parameters)
            for iproc in range(self.mesh_properties.nproc):
                # read database files
                keys, vals = sem.mread(path, self.model_parameters, iproc, prefix, suffix)
                minmax.update(keys, vals)

                if 'rho' not in keys:
                    key, val = sem.mread(path, ['rho'], iproc, prefix, suffix)
                    keys += key
                    vals += val

                # convert on the fly from one set of parameters to another
                mapped = self.map_forward(keys, vals)
                if PAR.DENSITY in ['Variable']:
                    pass
                else:
                    rho = mapped.pop('rho')
                for key, val in mapped.items():
                    model[key] += [val]

            if verbose:
                minmax.write(path, logpath)
            return model


#######original#######
#    def save(self, path, obj, prefix='', suffix=''):
#######original#######
#######Jiang change start#######
    def save(self, obj, path, parameters=['vp','vs','rho'], prefix='', suffix=''):
#######Jiang change end#######
        #print 'path', path
        unix.mkdir(path)
        model_init = join(PATH.OUTPUT, 'model_init')

        if 'kernel' in suffix:
            kernels = obj
            #print 'kernels', kernels
            # write kernels
            for iproc in range(self.mesh_properties.nproc):
                keys = kernels.keys()
                vals = []
                for key in keys:
                    vals += [kernels[key][iproc]]

                # write database files
                for key, val in zip(keys, vals):
                    sem.write(val, path, prefix+key+suffix, iproc)

        else:
            # write model
            model = obj
            #print 'model', model
            for iproc in range(self.mesh_properties.nproc):
                keys = model.keys()
                vals = []
                for key in keys:
                    vals += [model[key][iproc]]
                if 'rho' not in keys:
                    key, val = sem.mread(model_init, ['rho'], iproc, prefix, suffix)
                    keys += key
                    vals += val

                # convert on the fly from one set of parameters to another
                mapped = self.map_inverse(keys, vals)

                # write database files
                rho = mapped.pop('rho')
                if PAR.DENSITY == 'Variable':
                    sem.write(rho, path, prefix+'rho'+suffix, iproc)
                elif PAR.DENSITY == 'Constant':
                    sem.write(rho, path, prefix+'rho'+suffix, iproc)
                else:
                    rho = self.density_scaling(mapped.keys(), mapped.values())
                    sem.write(rho, path, prefix+'rho'+suffix, iproc)

                for key, val in mapped.items():
                    sem.write(val, path, prefix+key+suffix, iproc)


    def check_mesh_properties(self, path=None, parameters=None):
        if not parameters:
            parameters = self.model_parameters
        return super(elastic, self).check_mesh_properties(
            path, parameters)

    @property
    def parameters(self):
        return self.kernel_parameters
            

