import selenium
from selenium import webdriver
import pandas as pd
from page_parser import page_parser
from bank_dict import banks_dict
import joblib
from tqdm import tqdm
import unicodedata


class SravniParser:
    def __init__(self):
        self.banks = None
        CHROME_BIN_LOCATION = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
        CHROME_DRIVER_LOCATION = r'C:/Users/Lenovo/Downloads/chromedriver.exe'
        USER_DATA_DIR = r'C:\environments\selenium'

        options = selenium.webdriver.chrome.options.Options()
        service = selenium.webdriver.chrome.service.Service(CHROME_DRIVER_LOCATION)
        options.add_argument(f'user-data-dir={USER_DATA_DIR}')
        options.add_argument('--disable-popup-blocking')
        options.binary_location = CHROME_BIN_LOCATION
        self.driver = selenium.webdriver.Chrome(options=options, service=service)
        self.driver.maximize_window()

    def banks_init(self):
        try:
            banks = joblib.load('banks.pkl')
        except:
            banks = banks_dict(self.driver)
            joblib.dump(banks, 'banks.pkl', compress=1)
        self.banks = banks

    def get_all_rates(self):
        res = []
        for row in tqdm(self.banks):
            b = row['alias']
            n = row['name']
            try:
                res.append(page_parser(self.driver, b, n))
            except:
                print(f'Данные по {n} не найдены')
        return res


obj = SravniParser()
obj.banks_init()
res = obj.get_all_rates()


all_res = pd.concat(res,axis=0)

all_res['Сумма'] = all_res['Сумма'].apply(lambda x:unicodedata.normalize("NFKD",x))
all_res['Срок (в днях)'] = all_res['Срок (в днях)'].apply(lambda x:unicodedata.normalize("NFKD",str(x)))
all_res.to_excel(r'C:\Users\Lenovo\Documents\test_sravni.xlsx')