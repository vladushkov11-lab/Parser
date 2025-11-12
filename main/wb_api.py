import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from urllib.parse import urlparse, parse_qs
options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--window-size=1500,900")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_argument("--accept-language=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

def extract_article_from_url(url):
    try:
        # Разбираем URL
        parsed_url = urlparse(url)
        
        path_parts = parsed_url.path.split('/')
        
        # Ищем артикул в пути
        for part in path_parts:
            if part.isdigit() and len(part) >= 6:
                return int(part)
        
        if 'card' in parse_qs(parsed_url.query):
            card = parse_qs(parsed_url.query)['card'][0]
            if card.isdigit():
                return int(card)
                
        return None
        
    except Exception as e:
        print(f"Ошибка при разборе URL: {e}")
        return None

def parser_wildbox(art: int):
    """Парсит цену с Wildbox"""
    driver = None
    try:
        # Инициализация драйвера
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)
        driver.set_window_size(1500, 900)
        
        # Открываем страницу
        driver.get("https://wildbox.ru")
        logger.info("Страница Wildbox загружена")

        # Клик по кнопке "Личный кабинет"
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".t-btnflex__text")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)
        button.click()  # Используем обычный click
        logger.info("Кнопка 'Личный кабинет' нажата")

        # Ввод телефона
        phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='phone']")))
        phone_input.clear()
        phone_input.send_keys("(925) 068-14-11")
        logger.info("Телефон введён")

        # Ввод пароля
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Пароль']")))
        password_input.clear()
        password_input.send_keys("93eLgW7c")
        logger.info("Пароль введён")

        # Клик по кнопке входа
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        logger.info("Выполнен вход")
        
        # Ждем загрузки кабинета
        time.sleep(5)

        # Ищем поле ввода артикула
        articul_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Артикул или ссылка']"))
        )
        
        # Прокручиваем к полю ввода
        driver.execute_script("arguments[0].scrollIntoView(true);", articul_input)
        time.sleep(0.5)
        
        # Кликаем на поле
        articul_input.click()
        
        articul_input.clear()
        articul_input.send_keys(str(art))
        articul_input.send_keys(Keys.ENTER)
        logger.info(f"Артикул {art} введен и отправлен")

        # Ждем результат поиска
        wait = WebDriverWait(driver, 15)
        
        # Проверяем наличие цены
        price_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'ProductHeader_value__mc2rm') and contains(text(), '₽')]"))
        )
        
        price_text = price_element.text.strip()
        price_no_spp = price_text.replace('₽', '').replace(' ', '').strip()
        
        return price_no_spp

    except Exception as e:
        logger.error(f"Ошибка в parser_wildbox: {e}")
        if driver is not None:
            try:
                driver.save_screenshot(f"error_wildbox_{art}.png")
                logger.info("Скриншот сохранён")
            except:
                logger.error("Не удалось сделать скриншот")
        return None
        
    finally:
        # Безопасное закрытие драйвера
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Ошибка при закрытии драйвера: {e}")

def get_wb_price(article):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => false
        });
        window.navigator = {
        ...navigator,
        webdriver: false
        };
        Object.defineProperty(navigator, 'languages', {
        get: () => ['ru-RU', 'ru']
        });
        Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
        });
        """
})
        driver.get(f"https://www.wildberries.ru/catalog/{article}/detail.aspx")
        
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), '₽')]"))
        )
        price_text = price_element.text.strip()
        price = price_text.replace('₽', '').replace(' ', '')

        #ищем название
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3"))
        )
        name = name.text.strip()
        return {"price_spp": price, "name": name}
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
        
    finally:
        driver.quit()
def spp(price_no_spp: int, price_spp: int):
    spp = (1 - (price_no_spp/price_spp)) * 100
    spp = abs(spp)
    return spp
