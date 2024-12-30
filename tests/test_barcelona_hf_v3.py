import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from typing import Literal

from parameter_generator import generate_barcelona_hf_v3_parameters
from acribis_scores.barcelona_hf_v3 import calc_barcelona_hf_score, Parameters


class TestBarcelonaBioHF(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_barcelona_bio_hf(self):
        for i in range(10):
            parameters = generate_barcelona_hf_v3_parameters()
            r_score = self.__get_r_score(parameters)
            python_score = calc_barcelona_hf_score(parameters)
            p_le_wob = python_score['without_biomarkers']['life_expectancy']
            r_le_wob = r_score['without_biomarkers']['life_expectancy']
            try:
                p_le_wob = float(python_score['without_biomarkers']['life_expectancy'])
                r_le_wob = float(r_score['without_biomarkers']['life_expectancy'])
            except ValueError:
                pass
            self.assertEqual(p_le_wob, r_le_wob)

            if 'with_biomarkers' in python_score:
                p_le_wb = python_score['with_biomarkers']['life_expectancy']
                r_le_wb = r_score['with_biomarkers']['life_expectancy']
                try:
                    p_le_wb = float(python_score['with_biomarkers']['life_expectancy'])
                    r_le_wb = float(r_score['with_biomarkers']['life_expectancy'])
                except ValueError:
                    pass
                self.assertEqual(p_le_wb, r_le_wb)

            if 'with_biomarkers' in python_score:
                del python_score['with_biomarkers']['life_expectancy']
                del r_score['with_biomarkers']['life_expectancy']
            del python_score['without_biomarkers']['life_expectancy']
            del r_score['without_biomarkers']['life_expectancy']
            self.assertEqual(python_score, r_score)

    def __get_r_score(self, parameters: Parameters) -> dict[str, dict[str, None | float | str]]:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='Barcelona HF Score']").click()
        mapping_bool: dict[str, str] = {
            'Female': 'female',
            'Statin': 'statin',
            'ACEi/ARB': 'acei_arb',
            'Betablockers': 'betablocker',
            'Diabetes Mellitus': 'diabetes',
            'MRA': 'mra',
            'ICD': 'icd',
            'CRT': 'crt',
            'ARNI': 'arni',
            'SGLT2i': 'sglt2i'
        }
        mapping_number: dict[str, str] = {
            'Age (years)': 'barcelona_age',
            'Ejection fraction (%)': 'barcelona_ef',
            'Sodium (mmol/L)': 'sodium',
            'eGFR in mL/min/1.73m²': 'egfr',
            'Hemoglobin (g/dL)': 'hemoglobin',
            'Loop Diuretic Furosemide Dose': 'loop_diuretic',
            'HF Duration in months': 'hf_duration',
            'Hospitalisation Prev. Year': 'hosp_prev_year'
        }
        mapping_not_required: dict[Literal['NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)'], str] = {
            'NT-proBNP in pg/mL': 'nt_pro_bnp',
            'hs-cTnT in ng/L': 'hs_ctnt',
            'ST2 (ng/mL)': 'st2'
        }

        self.driver.find_elements(By.CSS_SELECTOR, ".selectize-input")[1].click()
        self.driver.find_element(By.CSS_SELECTOR,
                                 f"div[class*='option'][data-value='{parameters['NYHA Class']}']").click()
        for key, value in parameters.items():
            if key not in mapping_number:
                continue
            element = self.driver.find_element(By.ID, mapping_number[key])
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(str(value))
        for key, value in parameters.items():
            if key not in mapping_bool:
                continue
            if value != (self.driver.find_element(By.ID, mapping_bool[key]).get_attribute('checked') is not None):
                self.driver.find_element(By.ID, mapping_bool[key]).click()
        with_biomarkers = False
        for key in mapping_not_required:
            element = self.driver.find_element(By.ID, mapping_not_required[key])
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            if key in parameters:
                element.send_keys(str(parameters[key]))
                with_biomarkers = True
        self.driver.find_element(By.ID, "calculate_barcelona").click()
        WebDriverWait(self.driver, 5).until(
            text_to_be_present_in_element((By.ID, "score_output_barcelona"), "The calculated Barcelona HF scores are:"))
        text = self.driver.find_element(By.ID, "score_output_barcelona").text
        text = text.removeprefix('The calculated Barcelona HF scores are:\n')
        lines = text.split('\n')
        results = {line.split(' : ')[0]: line.split(' : ')[1] for line in lines}
        all_scores: dict[str, dict[str, None | list[float] | str]] = {'without_biomarkers': {'death': None,
                                                                                             'life_expectancy': None,
                                                                                             'hosp': None,
                                                                                             'hosp_death': None}}
        if with_biomarkers:
            all_scores['with_biomarkers'] = {'death': None,
                                             'life_expectancy': None,
                                             'hosp': None,
                                             'hosp_death': None}
        for key, value in results.items():
            value_list = []
            splitted = value.split(', ')
            if len(splitted) > 1:
                for v in splitted:
                    value_list.append(float(v))
            model_endpoint = key.split('$')
            all_scores[model_endpoint[0]][model_endpoint[1]] = value_list if len(value_list) > 0 else splitted[0]
        return all_scores


if __name__ == '__main__':
    unittest.main()
