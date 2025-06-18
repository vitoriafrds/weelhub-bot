from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import os
import json
import time
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


def login_with_credentials(driver: Chrome):
    logging.info('Iniciando preenchimento do formulario de login...')
    wait = WebDriverWait(driver, 15)

    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#username")))
    email_input.send_keys(os.getenv("WELLHUB_USERNAME"))

    continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#kc-form-login > div.button-wrapper > button")))
    continue_button.click()

    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#password")))
    password_input.send_keys(os.getenv("WELLHUB_PWD"))

    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#kc-form-login > div > div.gympass-button-wrapper.column-display > div > button")))
    login_button.click()
    logging.info('Login concluido.')

def open_classes_modal(driver):
    logging.info('Abrindo modal das turmas para buscar por checkins pendentes de validação')
    wait = WebDriverWait(driver, 20)

    checkins_to_confirm_menu = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#root > div > div > nav > ul:nth-child(1) > li:nth-child(2) > a > div > p")))
    checkins_to_confirm_menu.click()

def find_and_validate_checkins(driver: Chrome, classes_ids: list):
    open_classes_modal(driver)

    for radio_id in classes_ids:
        logging.info(f'Buscando checkins pendentes da turma: {radio_id}')
        radio = driver.find_element(By.ID, radio_id)
        radio.click()   

        wait = WebDriverWait(driver, 10)
        continue_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-koXPp.frGPhK")))
        continue_btn.click()

        validate_checkin(driver)
        open_classes_modal(driver)
    
def go_back_to_classes_modal(driver: Chrome):
    return driver.find_element(By.CSS_SELECTOR, "#app > div > div:nth-child(2) > main > header > div > div.Header-buttonBack-1M1L4 > span > span").click()

def check_for_ghost_checkin(driver: Chrome):
    logging.info("Validando se existe o checkin de onboarding da jornada de validação...")
    time.sleep(5)
    checkin_fantasma = driver.find_elements(By.CSS_SELECTOR, "#react-joyride-step-0 > div > div > div > div:nth-child(2) > div > button")

    if checkin_fantasma:
        for f in checkin_fantasma:
            f.click()
            logging.info("Checkin ficticio removido com sucesso, o processo seguirá corretamente...")
            time.sleep(2)
            driver.find_element(By.CSS_SELECTOR, "#modal > div > div > div > div > button:nth-child(2)").click()

def validate_checkin(driver: Chrome):
    check_for_ghost_checkin(driver)

    try:
        wait = WebDriverWait(driver, 10)
        botoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[span[text()='Confirm']]")))

        for botao in botoes:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", botao)
                logging.info("Checking encontrado...")
                wait.until(EC.element_to_be_clickable(botao))
                botao.click()

                logging.info("Checkins validados com sucesso")
                go_back_to_classes_modal(driver)
            except Exception as e:
                logging.error(f"Ocorreu um erro inesperado na tentativa de validar o checkin: {str(e)}")
                go_back_to_classes_modal(driver)
    except TimeoutException as error:
        logging.info("No momento não existem checkins para serem validados.")
        go_back_to_classes_modal(driver)

if __name__ == "__main__":
    week_days = {
        0: "seg",
        1: "ter",
        2: "qua",
        3: "qui",
        5: "sab"
    }

    classes_of_the_day = []
    week_day_code = datetime.date.today().weekday()
    current_weekday_name = week_days[week_day_code]
    
    logging.info(f'Iniciando processo de validação dos checkins das turmas de: {current_weekday_name}')

    with open("classes_calendar.json", 'r') as classes:
        data = json.load(classes)
        turmas = data.get(current_weekday_name.lower(), [])
        classes_of_the_day.extend(turmas)

    options = Options()  
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(os.getenv("WELLHUB_URL"))

    try:
        login_with_credentials(driver=driver)
        find_and_validate_checkins(driver=driver, classes_ids=classes_of_the_day)
    except Exception as error:
        logging.error(f"Ocorreu um erro inesperado: {str(error)}")
    finally:
        driver.quit()
        logging.info('Processo finalizado com sucesso')