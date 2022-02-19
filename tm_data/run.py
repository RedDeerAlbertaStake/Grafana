import json
import os
import subprocess
import time
from datetime import datetime

import requests
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

username = os.environ["TM_DATA_USERNAME"]
password = os.environ["TM_DATA_PASSWORD"]

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)


def get_tm():
    driver.get("https://tm.churchofjesuschrist.org")


def logout_tm():
    driver.get("https://tm.churchofjesuschrist.org/logout.html")


def do_username(username: str):
    username_box = driver.find_element(By.NAME, "username")
    username_box.send_keys(username)

    submit = driver.find_element(By.ID, "okta-signin-submit")
    submit.click()


def do_password(password: str):
    password_box = driver.find_element(By.NAME, "password")
    password_box.send_keys(password)

    verify = driver.find_elements(By.CLASS_NAME, "button-primary")

    try:
        verify[1].click()
    except:
        verify[0].click()


def do_mfa():
    mfa_dropdown = driver.find_element(By.CLASS_NAME, "option-selected")
    mfa_dropdown.click()

    mfa_select = driver.find_element(By.CLASS_NAME, "mfa-okta-verify-30")
    mfa_select.click()

    mfa_remember = driver.find_element(By.NAME, "rememberDevice")
    mfa_remember.send_keys(Keys.SPACE)

    mfa_send_push = driver.find_elements(By.CLASS_NAME, "button-primary")

    try:
        mfa_send_push[1].click()
    except:
        mfa_send_push[0].click()


def wait_on_tm_after_auth():
    WebDriverWait(driver, 600).until(
        EC.url_contains("https://tm.churchofjesuschrist.org")
    )

    time.sleep(10)


def get_security_token():
    tm_user_session = json.loads(
        driver.execute_script("return sessionStorage.getItem('tmUserSession');")
    )

    return tm_user_session["securityToken"]


def terraform_init():
    subprocess.check_call(
        ["terraform", "init"],
    )


def terraform_apply():
    subprocess.check_call(
        ["terraform", "apply", "-auto-approve"],
    )


def main():
    with open("/app/config/app.yaml", "r") as f:
        config = yaml.safe_load(f.read())

    terraform_init()

    get_tm()

    WebDriverWait(driver, 10).until(EC.url_to_be("https://id.churchofjesuschrist.org/"))

    driver.implicitly_wait(30)

    do_username(username=username)
    do_password(password=password)
    do_mfa()

    wait_on_tm_after_auth()

    while True:
        headers = {
            "Authorization": f"Bearer {get_security_token()}",
        }

        data = {"chapels": {}}

        for serial in config["firewall"]["serials"]:
            r = requests.get(
                f"https://tm.churchofjesuschrist.org/api/meraki/activate/{serial}",
                headers=headers,
            )

            r_subnet = requests.get(
                f"https://tm.churchofjesuschrist.org/api/meraki/firewall/{serial}/subnets",
                headers=headers,
            )

            chapelName = r.json()["propertyName"]
            chapelIp = r_subnet.json()["publicIp"]

            data["chapels"][chapelName] = chapelIp

        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print(json.dumps(data, indent=2))

        with open("chapels.auto.tfvars.json", "w") as f:
            json.dump(data, f, indent=2)

        logout_tm()

        terraform_apply()

        time.sleep(600)

        get_tm()
        do_username(username=username)
        do_password(password=password)

        wait_on_tm_after_auth()


if __name__ == "__main__":
    main()
