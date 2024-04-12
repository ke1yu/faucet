from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions  # Import for Chrome options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from twocaptcha import TwoCaptcha
import os


DOGE = 'doge'
LITE = 'lite'
TRON = 'tron'
SITE_LIST = [DOGE, TRON]

URL_DICT = {
    DOGE: 'https://dogeking.io/',
    LITE: 'https://liteking.io/',
    TRON: 'https://tronking.io/'
}

LOGIN_URL = 'login.php'
GAMES_URL = 'games.php'

TWOCAPTCHA_API_KEY = os.environ['TWOCAPTCHA_API_KEY']

SITEKEY_DICT = {
    DOGE: os.environ['DOGE_SITE_KEY'],
    LITE: os.environ['LITE_SITE_KEY'],
    TRON: os.environ['TRON_SITE_KEY'],
}

MAIL_ADDRESS = os.environ['MAIL_ADDRESS']

PASSWORD_DICT = {
    DOGE: os.environ['DOGE_PASSWORD'],
    LITE: os.environ['LITE_PASSWORD'],
    TRON: os.environ['TRON_PASSWORD']
}


def solve_captcha(driver, sitekey, url):
  solver = TwoCaptcha(TWOCAPTCHA_API_KEY)
  try:
    print('Solving captcha...')
    response = solver.recaptcha(sitekey=sitekey, url=url)
    print('Captcha solved successfully')
    code = response['code']
    recaptcha_response_element = driver.find_element(By.ID,
                                                     'g-recaptcha-response')
    driver.execute_script(f'arguments[0].value = "{code}";',
                          recaptcha_response_element)
  except Exception as e:
    print('Captcha unsolvable', e)


# def solve_turnstile(driver, sitekey, url):
#   solver = TwoCaptcha(TWOCAPTCHA_API_KEY)
#   # try:
#   script = 'const i = setInterval(()=>{if (window.turnstile) {clearInterval(i) window.turnstile.render = (a,b) => {let p = {method: "turnstile",key: "YOUR_API_KEY",sitekey: b.sitekey,pageurl: window.location.href,data: b.cData,pagedata: b.chlPageData,action: b.action,userAgent: navigator.userAgent,json: 1}console.log(JSON.stringify(p))window.tsCallback = b.callbackreturn "foo"}}},50)'
#   site_params = driver.execute_script(script)
#   print(site_params)
#   response = solver.turnstile(sitekey=sitekey, url=url, action='managed', data=LITE_CF_DATA, pagedata=LITE_CF_PAGEDATA)
#   print('Turnstile solved successfully')
#   # code = response['code']
#   # turnstile_response_element = driver.find_element(By.NAME, 'cf-turnstile-response')
#   # driver.execute_script(f'arguments[0].value = "{code}";', turnstile_response_element)
#   # except Exception as e:
#   #   print('Turnstile unsolvable', e)


def login(driver, site):
  driver.find_element(By.CSS_SELECTOR,'input[id="user_email"]').send_keys(MAIL_ADDRESS)
  driver.find_element(By.CSS_SELECTOR,'input[id="password"]').send_keys(PASSWORD_DICT[site])
  solve_captcha(driver, SITEKEY_DICT[site], URL_DICT[site])
  login_btn = driver.find_element(By.CSS_SELECTOR,
                                  'button[id="process_login"]')
  login_btn.click()


def spin(driver, site):
  modal_wait = WebDriverWait(driver, 30)
  modal_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="select_game"]')))
  driver.execute_script('javascript:show_spin_modal()')
  spin_btn = driver.find_element(By.CSS_SELECTOR, 'button[id="spin_wheel"]')
  try:
    before_wait = WebDriverWait(driver, 60)
    before_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="spin_wheel"]')))
    if spin_btn.is_enabled():
      solve_captcha(driver, SITEKEY_DICT[site], URL_DICT[site] + GAMES_URL)
      
      spin_btn.click()
      after_wait = WebDriverWait(driver, 10)
      after_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jq-toast-heading")))
  except TimeoutException:
    print('TimeoutException')
    

def selenium_task():
  options = ChromeOptions()  # Change to ChromeOptions
  options.add_argument("--headless=new")
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")

  # Perform the selenium task
  with webdriver.Chrome(options=options) as driver:
    driver.implicitly_wait(10)
    for site in SITE_LIST:
      login_page_url = URL_DICT[site] + LOGIN_URL
      driver.get(login_page_url)
      assert "king" in driver.title
      if driver.current_url == login_page_url:
        login(driver, site)
      spin(driver, site)


if __name__ == '__main__':
  selenium_task()
