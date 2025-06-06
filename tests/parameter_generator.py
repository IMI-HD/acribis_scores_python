import random
from typing import Any, get_type_hints, Mapping, get_origin, NotRequired, Annotated

from acribis_scores import *
from acribis_scores.value_range import ValueRange


def __get_random_parameters(parameter_dict: Mapping[str, Any]) -> dict[str, Any]:
    types = get_type_hints(parameter_dict)
    random_parameters = {}
    for key, annotation in get_type_hints(parameter_dict, include_extras=True).items():
        raw_parameter = types[key]

        if get_origin(annotation) is NotRequired and bool(random.getrandbits(1)):
            continue

        metadata = getattr(annotation, '__metadata__', None)
        minimum = 0
        maximum = 100000
        if metadata:
            minimum = metadata[0].min
            maximum = metadata[0].max
        if raw_parameter == int:
            random_parameters[key] = random.randint(minimum, maximum)
        elif raw_parameter == float:
            random_parameters[key] = random.uniform(minimum, maximum)
        elif raw_parameter == bool:
            random_parameters[key] = bool(random.getrandbits(1))
        else:
            random_parameters[key] = None
    return random_parameters


def generate_chads_vasc_parameters() -> chads_vasc.Parameters:
    random_parameters = __get_random_parameters(chads_vasc.Parameters)
    if random_parameters['Age ≥75y']:
        random_parameters['Age 65-74y'] = False
    return random_parameters


def generate_has_bled_parameters() -> has_bled.Parameters:
    return __get_random_parameters(has_bled.Parameters)


def generate_abc_af_bleeding_parameters() -> abc_af_bleeding.Parameters:
    random_parameters: abc_af_bleeding.Parameters = __get_random_parameters(abc_af_bleeding.Parameters)
    x = bool(random.getrandbits(1))
    random_parameters['DOAC'] = x
    random_parameters['Aspirin'] = not x
    return random_parameters


def generate_abc_af_stroke_parameters() -> abc_af_stroke.Parameters:
    random_parameters: abc_af_stroke.Parameters = __get_random_parameters(abc_af_stroke.Parameters)
    x = bool(random.getrandbits(1))
    random_parameters['DOAC'] = x
    random_parameters['Aspirin'] = not x
    return random_parameters


def generate_abc_af_death_parameters() -> abc_af_death.Parameters:
    return __get_random_parameters(abc_af_death.Parameters)


def generate_charge_af_parameters() -> charge_af.Parameters:
    return __get_random_parameters(charge_af.Parameters)


def generate_smart_parameters(creatinine: float) -> smart.Parameters:
    random_parameters = __get_random_parameters(smart.Parameters)
    egfr = 186 * creatinine ** (-1.154) * random_parameters['Age in years'] ** (-0.203)
    if not random_parameters['Male']:
        egfr *= 0.742
    cvds: list[bool] = [bool(random.getrandbits(1)) for _ in range(4)]
    if not any(cvds):
        cvds[random.randint(0, 3)] = True
    random_parameters['History of coronary artery disease'] = cvds[0]
    random_parameters['History of cerebrovascular disease'] = cvds[1]
    random_parameters['Abdominal aortic aneurysm'] = cvds[2]
    random_parameters['Peripheral artery disease'] = cvds[3]
    random_parameters['eGFR in mL/min/1.73m²'] = egfr
    return random_parameters


def generate_smart_reach_parameters() -> smart_reach.Parameters:
    random_parameters = __get_random_parameters(smart_reach.Parameters)
    cvds: list[bool] = [bool(random.getrandbits(1)) for _ in range(3)]
    if not any(cvds):
        cvds[random.randint(0, 2)] = True
    random_parameters['History of coronary artery disease'] = cvds[0]
    random_parameters['History of cerebrovascular disease'] = cvds[1]
    random_parameters['Peripheral artery disease'] = cvds[2]
    return random_parameters


def generate_maggic_parameters() -> maggic.Parameters:
    return __get_random_parameters(maggic.Parameters)


def generate_barcelona_hf_v3_parameters() -> barcelona_hf_v3.Parameters:
    # noinspection PyTypedDict
    barcelona_hf_v3.Parameters.__annotations__ = {
        'Age (years)': Annotated[int, ValueRange(32, 90)],
        'Female': bool,
        'NYHA Class': Annotated[int, ValueRange(1, 4)],
        'Ejection fraction (%)': Annotated[int, ValueRange(13, 78)],
        'Sodium (mmol/L)': Annotated[int, ValueRange(128, 145)],
        'eGFR in mL/min/1.73m²': Annotated[int, ValueRange(8, 119)],
        'Hemoglobin (g/dL)': Annotated[float, ValueRange(9, 16)],
        'Loop Diuretic Furosemide Dose': Annotated[int, ValueRange(0, 100)],
        'Statin': bool,
        'ACEi/ARB': bool,
        'Betablockers': bool,
        'HF Duration in months': Annotated[int, ValueRange(1, 257)],
        'Diabetes Mellitus': bool,
        'Hospitalisation Prev. Year': Annotated[int, ValueRange(0, 5)],
        'MRA': bool,
        'ICD': bool,
        'CRT': bool,
        'ARNI': bool,
        'NT-proBNP in pg/mL': NotRequired[Annotated[int, ValueRange(38, 34800)]],
        'hs-cTnT in ng/L': NotRequired[Annotated[float, ValueRange(4.8245, 242.84)]],
        'ST2 (ng/mL)': NotRequired[Annotated[float, ValueRange(6.29, 171.1)]],
        'SGLT2i': bool
    }
    parameters = __get_random_parameters(barcelona_hf_v3.Parameters)
    if parameters['ACEi/ARB']:
        parameters['ARNI'] = False
    return parameters
