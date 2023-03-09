import re
import time

from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from tqdm import tqdm
import unicodedata

def page_parser(driver,bank, bank_name):
    baseurl = fr"https://www.sravni.ru/biznes-vklady/bank/{bank}/"
    driver.get(baseurl)
    # XPATH = r'/html/body/div[1]/div[4]/div/div[1]/div/div[1]/div[2]/button/span'


    def show_all():
        XPATH = r'/html/body/div[1]/div[5]/div[3]/div[2]/button'
        while True:
            try:
                el = driver.find_element(By.XPATH, XPATH)
                driver.execute_script('window.scroll(0,document.body.scrollHeight)')
                driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', el)
                driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', el)
                driver.execute_script('arguments[0].click();', el)
            except (StaleElementReferenceException, NoSuchElementException) as e:
                break
        driver.execute_script('window.scroll({top:0})')

    def get_bank_info(source):
        tbl = pd.read_html(source)[0]
        soup = bs(source, features="lxml")
        regex = re.compile('ProductInfo_tabRow.*')
        ls = soup.find_all('div', {'class': regex})
        regex1 = re.compile('ProductInfo_subCaption.*')
        nm = soup.find_all('div', {'class': regex1})
        nm = unicodedata.normalize("NFKD", nm[0].attrs['title'])
        needed = ['Условия досрочного расторжения', 'Условия пополнения депозита', 'Дополнительные опции ',
                  'Выплаты процентов']
        for t in ls:
            n = unicodedata.normalize("NFKD", t.contents[0].text)  # attr name
            v = unicodedata.normalize("NFKD", t.contents[1].text)  # attr value
            if n in needed:
                tbl[n] = v
        tbl['тип'] = nm
        return tbl

    # product_path = lambda x: fr'/html/body/div[1]/div[3]/div[2]/div[1]/div[{x}]/div[1]/div'

    res = []
    show_all()
    time.sleep(3)
    els = driver.find_elements(By.XPATH, '//div[contains(@class, "style_card")]')
    print(bank_name)
    for i in range(len(els)):
        driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', els[i])
        driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', els[i])
        els[i].click()
        src = driver.find_element(By.XPATH, "//body").get_attribute('outerHTML')
        res.append(get_bank_info(src))
        el1 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/span')
        el1.click()

    concated = pd.concat(res, axis=0)
    concated['банк'] = bank_name
    return concated

