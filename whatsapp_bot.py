# importing all the necessary libaries
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os
from PIL import Image
from flask import Flask, send_from_directory

from webdriver_manager.chrome import ChromeDriverManager


# setup chrome for selenium (needed for heroku builds)
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

app = Flask(__name__)


@app.route("/")
def main_page():
    browser.save_screenshot("./img/name.png")
    return send_from_directory("img", path="name.png")


def run_web_app():
    app.run()


s = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=s)
browser.get('https://web.whatsapp.com/')
wait = WebDriverWait(browser, 1000)
t = threading.Thread(target=run_web_app)
t.start()
try:
    os.makedirs("./img/")
except FileExistsError:
    pass
for x in range(0, 5):
    wait = WebDriverWait(browser, 10000)
# screenshot = Image.open("./img/name.png")
# screenshot.show()
target = '"Avi sending stuff"'  # enter contact name here
string = "Hello World!"  # target msg
x_arg = ' //span[contains(@title, ' + target + ')]'
print("started whatsapp")
target = wait.until(ec.presence_of_element_located((By.XPATH, x_arg)))
print("located contact")
target.click()

x_arg = "//div[@title='Type a message']"
input_box = wait.until(ec.presence_of_element_located((By.XPATH, x_arg)))
print("found message box")
for i in range(50):
    input_box.send_keys(string + Keys.ENTER)
