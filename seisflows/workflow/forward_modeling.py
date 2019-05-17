
import sys
import numpy as np

from seisflows.config import ParameterError, custom_import
from seisflows.tools import unix
from seisflows.plugins import wavelets
from seisflows.plugins.signal import sbandpass, sconvolve

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']
preprocess = sys.modules['seisflows_preprocess']


class forward_modeling(custom_import('workflow', 'test_forward')):
   pass
