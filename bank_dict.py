from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup as bs
import re


def banks_dict(driver, save=True):
    baseurl = r"https://www.sravni.ru/banki/?tag=businessDeposits"
    driver.get(baseurl)

    XPATH = r'/html/body/div[1]/div[4]/div/div[1]/div/div[1]/div[2]/button'
    el = driver.find_element(By.XPATH, XPATH)
    while True:
        try:
            driver.execute_script('window.scroll(0,document.body.scrollHeight)')
            driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', el)
            driver.execute_script('window.scroll({top:arguments[0].getBoundingClientRect().top - 20})', el)
            driver.execute_script('arguments[0].click();', el)
        except StaleElementReferenceException:
            break

    src = driver.find_element(By.XPATH, "//body").get_attribute('outerHTML')

    soup = bs(src)
    regex = re.compile('card_wrapper.*')
    ls = soup.find_all('div', {'class': regex})

    def get_banks(banks_list):
        res = []
        for b in banks_list:
            n = str(b.contents[0].contents[0].contents[0].contents[1].contents[0].contents[0].contents[0])  # bank name
            a = b.contents[0].contents[0].contents[0].contents[0].attrs['href'].split('/')[-2]  # bank alias
            res.append({'name': n, 'alias': a, 'href': f'https://www.sravni.ru/biznes-vklady/bank/{a}/'})
        return res

    return get_banks(ls)

