
from seisflows.config import custom_import


class ChenTromp_vti(custom_import('solver', 'ChenTromp_base')):

    # model parameters included in inversion
    parameters = []
    parameters += ['A']
    parameters += ['C']
    parameters += ['L']
    parameters += ['N']
    parameters += ['F']

