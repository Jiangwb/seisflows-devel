
from seisflows.config import custom_import

class ChenTromp_hti(custom_import('solver', 'ChenTromp_base')):

    # model parameters included in inversion
    parameters = []
    parameters += ['A']
    parameters += ['C']
    parameters += ['L']
    parameters += ['N']
    parameters += ['F']
    parameters += ['Gc']
    parameters += ['Gs']
    parameters += ['Bc']
    parameters += ['Bs']
    parameters += ['Hc']
    parameters += ['Hs']
    parameters += ['Ec']
    parameters += ['Es']

