import pytest
import pathlib
import json

from sympy_adc.func import import_from_sympy_latex


@pytest.fixture(scope='session')
def cls_instances():
    from sympy_adc.groundstate import Operators, GroundState
    from sympy_adc.isr import IntermediateStates
    from sympy_adc.secular_matrix import SecularMatrix

    mp_op = Operators(variant='mp')
    mp = GroundState(mp_op, first_order_singles=False)
    isr_pp = IntermediateStates(mp, variant='pp')
    m_pp = SecularMatrix(isr_pp)
    return {
        'mp': {
            'op': mp_op,
            'gs': mp,
            'isr': isr_pp,
            'm': m_pp
        },
        're': {
            'op': Operators(variant='re'),
        }
    }


@pytest.fixture(scope='session')
def reference_data() -> dict[int, dict]:

    def import_data_strings(data_dict: dict) -> dict:
        ret = {}
        for key, val in data_dict.items():
            if isinstance(val, dict):
                ret[key] = import_data_strings(val)
            elif isinstance(val, str):
                ret[key] = import_from_sympy_latex(val)
            else:
                raise TypeError(f"Unknown type {type(val)}.")
        return ret

    def hook(d): return {int(key) if key.isnumeric() else key: val
                         for key, val in d.items()}

    cache = {}

    path_to_data = pathlib.Path(__file__).parent / 'reference_data'
    for jsonfile in path_to_data.glob('*.json'):
        data = json.load(open(jsonfile), object_hook=hook)
        name = jsonfile.name.split('.json')  # remove .json extension
        assert len(name) == 2
        cache[name[0]] = import_data_strings(data)
    return cache
