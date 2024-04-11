from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions  # Import for Chrome options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import os

print(1)
DOGE = 'doge'
LITE = 'lite'
TRON = 'tron'
SITE_LIST = [DOGE, TRON]
print(2)
URL_DICT = {
    DOGE: 'https://dogeking.io/',
    LITE: 'https://liteking.io/',
    TRON: 'https://tronking.io/'
}

LOGIN_URL = 'login.php'
GAMES_URL = 'games.php'

TWOCAPTCHA_API_KEY = os.environ.get('TWOCAPTCHA_API_KEY')

SITEKEY_DICT = {
    DOGE: os.environ.get('DOGE_SITE_KEY'),
    LITE: os.environ.get('LITE_SITE_KEY'),
    TRON: os.environ.get('TRON_SITE_KEY'),
}

MAIL_ADDRESS = os.environ.get('MAIL_ADDRESS')

PASSWORD_DICT = {
    DOGE: os.environ.get('DOGE_PASSWORD'),
    LITE: os.environ.get('LITE_PASSWORD'),
    TRON: os.environ.get('TRON_PASSWORD')
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
  print(6.5)
  print(SITE_LIST)
  driver.find_element(By.CSS_SELECTOR,'input[id="user_email"]').send_keys(MAIL_ADDRESS)
  print(6.6)
  print(PASSWORD_DICT)
  driver.find_element(By.CSS_SELECTOR,'input[id="password"]').send_keys(PASSWORD_DICT[site])
  print(SITEKEY_DICT)
  print(6.7)
  solve_captcha(driver, SITEKEY_DICT[site], URL_DICT[site])
  print(7)
  login_btn = driver.find_element(By.CSS_SELECTOR,
                                  'button[id="process_login"]')
  print(8)
  login_btn.click()


def spin(driver, site):
  spin_btn = driver.find_element(By.CSS_SELECTOR, 'button[id="spin_wheel"]')
  if spin_btn.is_enabled():
    driver.execute_script('javascript:show_spin_modal()')
    solve_captcha(driver, SITEKEY_DICT[site], URL_DICT[site] + GAMES_URL)
    spin_btn.click()


def selenium_task():
  options = ChromeOptions()  # Change to ChromeOptions
  options.add_argument("--headless")
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")

  # Perform the selenium task
  try:
    with webdriver.Chrome(options=options) as driver:
      driver.implicitly_wait(10)
      print(3)
      print(SITE_LIST)
      for site in SITE_LIST:
        login_page_url = URL_DICT[site] + LOGIN_URL
        print(4)
        driver.get(login_page_url)
        assert "king" in driver.title
        if driver.current_url == login_page_url:
          print(5)
          login(driver, site)
          print(6)
        spin(driver, site)
      wait = WebDriverWait(driver, 10)
      wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jq-toast-heading")))
  except Exception as e:
    print(e)


if __name__ == '__main__':
  selenium_task()
