
from seisflows.config import custom_import


class ChenTromp_tti(custom_import('solver', 'ChenTromp_base')):

    # model parameters included in inversion
    parameters = []
    parameters += ['A']
    parameters += ['C']
    parameters += ['L']
    parameters += ['N']
    parameters += ['F']
    parameters += ['Jc']
    parameters += ['Js']
    parameters += ['Kc']
    parameters += ['Ks']
    parameters += ['Mc']
    parameters += ['Ms']
    parameters += ['Gc']
    parameters += ['Gs']
    parameters += ['Bc']
    parameters += ['Bs']
    parameters += ['Hc']
    parameters += ['Hs']
    parameters += ['Dc']
    parameters += ['Ds']
    parameters += ['Ec']
    parameters += ['Es']

