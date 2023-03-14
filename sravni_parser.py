import numpy as np
import selenium
from selenium import webdriver
import pandas as pd
from page_parser import page_parser
from bank_dict import banks_dict
import joblib
from tqdm import tqdm
import unicodedata
from numpy import vectorize


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
        self.s_list = [1e5, 10e5, 30e5, 100e5, 500e5, 999e5]
        self.d_list = [1, 3, 4, 6, 7, 14, 21, 31, 61, 92, 122, 153, 183, 274, 366, 549, 731, 1096]

    def close(self):
        self.driver.close()

    def banks_init(self):
        try:
            banks = joblib.load('banks.pkl')
        except:
            banks = banks_dict(self.driver)
            joblib.dump(banks, 'banks.pkl', compress=1)
        self.banks = banks

    def get_all_rates(self, bank=None):
        res = []
        if bank is None:
            for row in tqdm(self.banks):
                b = row['alias']
                n = row['name']
                try:
                    res.append(page_parser(self.driver, b, n))
                except:
                    print(f'Данные по {n} не найдены')
        else:
            b = bank
            n = bank
            try:
                res.append(page_parser(self.driver, b, n))
            except:
                print(f'Данные по {n} не найдены')
        return res

    def data_preprocessing(self, data):
        def to_int(vals):
            return [int(v.replace('₽', '').replace('€', '').replace('$', '').replace(' ', '')) for v in vals]

        @vectorize
        def splitter(x):
            if chr(8211) in str(x):
                return str(x).split(chr(8211)) if isinstance(x, (int, float)) else x.split(chr(8211))
            elif 'от' in str(x):
                return [str(x).replace('от', ''), '1000000000000']
            elif 'до' in str(x):
                return ['1', str(x).replace('до', '')]
            else:
                return [str(x), str(x)]

        @vectorize
        def checker(x, v):
            r1, r2 = to_int(splitter(x))
            if r1 <= v <= r2:
                return v
            else:
                return None

        @vectorize
        def b_checker(x, v, t):
            r1, r2 = to_int(splitter(x))
            if v < r2 and t:
                return f'свыше {v}'
            elif v > r1 and not t:
                return f'менее {v}'
            elif r1 <= v <= r2:
                return v
            else:
                return None

        def value_splitter(df, val_name, vals):
            dfs = []

            for v in tqdm(vals):
                v = int(v)
                df1 = df.copy()

                res = df1[val_name].apply(lambda x: checker(x, v))
                df1[f'{val_name} дискр.'] = res

                dfs.append(df1)
            result = pd.concat(dfs).drop_duplicates().reset_index(drop=True)
            return result[result[f'{val_name} дискр.'].notna()].reset_index(drop=True)

        n_data = value_splitter(data, 'Сумма', self.s_list)

        n_data = value_splitter(n_data, 'Срок (в днях)', self.d_list)

        n_data['Ставка'] = n_data['Ставка'].apply(lambda x: x.replace('%', '').replace(',', '.')) \
            .replace(chr(8211), '') \
            .replace(chr(8212), np.NaN) \
            .astype(float)
        n_data['Ставка при открытии онлайн'] = n_data['Ставка при открытии онлайн'].apply(
            lambda x: x.replace('%', '').replace(',', '.')) \
            .replace(chr(8211), '') \
            .replace(chr(8212), np.NaN) \
            .astype(float)
        return n_data


if __name__ == '__main__':
    obj = SravniParser()
    obj.banks_init()
    obj.close()
    results = obj.get_all_rates()
    all_res = pd.concat(results, axis=0)
    all_res['Сумма'] = all_res['Сумма'].apply(lambda x: unicodedata.normalize("NFKD", x))
    all_res['Срок (в днях)'] = all_res['Срок (в днях)'].apply(lambda x: unicodedata.normalize("NFKD", str(x)))
    n_data = obj.data_preprocessing(all_res)

n_data.to_csv(r'C:/Users/Lenovo/Downloads/sravni.csv')