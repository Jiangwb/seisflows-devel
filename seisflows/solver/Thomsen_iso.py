
from seisflows.config import custom_import


class Thomsen_iso(custom_import('solver', 'Thomsen_base')):

    # model parameters included in inversion
    parameters = []
    parameters += ['vp']
    parameters += ['vs']

