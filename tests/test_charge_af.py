import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from parameter_generator import generate_charge_af_parameters
from acribis_scores.charge_af import calc_charge_af_score, Parameters


@unittest.skip("Not yet fully implemented")
class TestCHARGEAFCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_charge_af(self):
        for i in range(10):
            parameters = generate_charge_af_parameters()
            print(f"Run {i + 1}:\n{parameters}")

            r_score = self.__get_r_score(parameters)
            python_score = calc_charge_af_score(parameters)
            self.assertEqual(round(python_score, 2), r_score, 'CHARGE-AF')

    def __get_r_score(self, parameters: Parameters) -> float:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='CHARGE-AF Score']").click()
        mapping: dict[str, str] = {
            'Race (white)': 'race_white',
            'Smoking (current)': 'smoking_current',
            'Antihypertensive Medication Use (Yes)': 'antihypertensive_use',
            'Diabetes (Yes)': 'diabetes_yes',
            'Heart failure (Yes)': 'heart_failure_yes',
            'Myocardial infarction (Yes)': 'mi_yes'
        }
        element = self.driver.find_element(By.ID, "charge_af_age")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Age']))
        element = self.driver.find_element(By.ID, "height")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Height']))
        element = self.driver.find_element(By.ID, "weight")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Weight']))
        element = self.driver.find_element(By.ID, "systolic_bp")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Systolic Blood Pressure']))
        element = self.driver.find_element(By.ID, "diastolic_bp")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Diastolic Blood Pressure']))
        for key, value in parameters.items():
            if key not in mapping:
                continue
            if value != (self.driver.find_element(By.ID, mapping[key]).get_attribute('checked') is not None):
                self.driver.find_element(By.ID, mapping[key]).click()
        self.driver.find_element(By.ID, "calculate_charge_af").click()
        text = self.driver.find_element(By.ID, "score_output_charge_af").text
        return float(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
