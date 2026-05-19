import os
import time
import random
import re
import subprocess
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from get_registration_link import get_aws_registration_link


def get_verification_code_from_email(start_time, max_attempts=2, delay=5):
    """
    Получает код верификации из последнего письма от AWS

    Args:
        start_time: datetime объект с временем начала регистрации
        max_attempts: максимальное количество попыток
        delay: задержка между попытками в секундах

    Returns:
        str: код верификации или None если не найден
    """
    # Форматируем дату для поиска в Gmail (YYYY/MM/DD)
    date_filter = start_time.strftime("%Y/%m/%d")

    for attempt in range(1, max_attempts + 1):
        print(f"Попытка {attempt}/{max_attempts}: Проверяю почту на наличие письма от AWS...")

        try:
            # Ищем письма от AWS после указанной даты
            result = subprocess.run(
                ['gog', 'gmail', 'search', f'from:no-reply@signin.aws after:{date_filter}', '--limit', '1'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Ошибка при поиске писем: {result.stderr}")
                if attempt < max_attempts:
                    print(f"Жду {delay} секунд перед следующей попыткой...")
                    time.sleep(delay)
                continue

            # Извлекаем ID письма из вывода
            lines = result.stdout.strip().split('\n')
            message_id = None
            for line in lines:
                if line and not line.startswith('#') and not line.startswith('ID'):
                    parts = line.split()
                    if parts:
                        message_id = parts[0]
                        break

            if not message_id:
                print("Письмо от AWS ещё не пришло")
                if attempt < max_attempts:
                    print(f"Жду {delay} секунд перед следующей попыткой...")
                    time.sleep(delay)
                continue

            print(f"Найдено письмо с ID: {message_id}")

            # Получаем содержимое письма
            result = subprocess.run(
                ['gog', 'gmail', 'get', message_id],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Ошибка при получении письма: {result.stderr}")
                if attempt < max_attempts:
                    print(f"Жду {delay} секунд перед следующей попыткой...")
                    time.sleep(delay)
                continue

            email_content = result.stdout

            # Извлекаем код верификации (6 цифр)
            # Ищем паттерны: "Verification code: 123456" или "code: 123456" или просто "123456"
            code_patterns = [
                r'Verification code:?\s*(\d{6})',
                r'verification code:?\s*(\d{6})',
                r'code:?\s*(\d{6})',
                r'\b(\d{6})\b'
            ]

            for pattern in code_patterns:
                match = re.search(pattern, email_content, re.IGNORECASE)
                if match:
                    code = match.group(1)
                    print(f"Найден код верификации: {code}")
                    return code

            print("Код верификации не найден в письме")
            if attempt < max_attempts:
                print(f"Жду {delay} секунд перед следующей попыткой...")
                time.sleep(delay)

        except subprocess.TimeoutExpired:
            print("Таймаут при выполнении команды gog")
            if attempt < max_attempts:
                print(f"Жду {delay} секунд перед следующей попыткой...")
                time.sleep(delay)
        except Exception as e:
            print(f"Ошибка при получении кода: {e}")
            if attempt < max_attempts:
                print(f"Жду {delay} секунд перед следующей попыткой...")
                time.sleep(delay)

    return None


def main():
    # Фиксируем время начала регистрации
    start_time = datetime.now()
    print(f"Время начала регистрации: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Получаем ссылку регистрации от omniroute
    print("Получаю ссылку регистрации от omniroute...")
    link_data = get_aws_registration_link()

    if not link_data or not link_data.get('url'):
        print("Ошибка: не удалось получить ссылку регистрации от omniroute")
        return

    target_url = link_data['url']
    device_code = link_data['device_code']
    user_code = link_data['user_code']

    print(f"Получена ссылка: {target_url}")
    print(f"Device code: {device_code}")
    print(f"User code: {user_code}")
    print(f"Expires in: {link_data['expires_in']} seconds")

    # Email для ввода
    email = "pavlo.trach@scriptium.uk"

    # Полное имя для ввода
    full_name = "Pavlo Trach"

    # Создаём папки если их нет
    os.makedirs("screenshot", exist_ok=True)
    os.makedirs("page_code", exist_ok=True)

    print(f"Открываю страницу: {target_url}")

    # Настройки для undetected-chromedriver
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new')  # Отключаем headless режим для GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')

    # Используем ExpressVPN SOCKS5 прокси (USA New York)
    # options.add_argument('--proxy-server=socks5://127.0.0.1:3114')

    # Создаём драйвер (без указания версии - автоопределение)
    driver = uc.Chrome(options=options)

    # Функция для имитации движения мыши
    def human_mouse_move(driver):
        try:
            actions = ActionChains(driver)
            # Небольшие случайные движения мыши
            for _ in range(random.randint(1, 2)):
                x_offset = random.randint(10, 50)
                y_offset = random.randint(10, 50)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
        except:
            pass  # Игнорируем ошибки движения мыши в headless режиме
        time.sleep(random.uniform(0.5, 1.0))

    # Функция для имитации скролла
    def human_scroll(driver):
        try:
            # Скролл вниз
            driver.execute_script("window.scrollBy(0, %d);" % random.randint(100, 300))
            time.sleep(random.uniform(0.5, 1.0))
            # Скролл вверх
            driver.execute_script("window.scrollBy(0, %d);" % random.randint(-100, -50))
            time.sleep(random.uniform(0.5, 1.0))
        except:
            pass

    # Функция для имитации чтения страницы
    def human_read_page(driver):
        print("Имитация чтения страницы...")
        human_scroll(driver)
        time.sleep(random.uniform(1, 2))
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

    try:
        # Переходим по URL
        driver.get(target_url)
        print("Страница загружена")

        # Ждём загрузки страницы и имитируем чтение
        time.sleep(random.uniform(2, 3))
        human_read_page(driver)

        # Принимаем куки если баннер есть
        try:
            accept_cookies = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-id="awsccc-cb-btn-accept"]'))
            )
            accept_cookies.click()
            print("Куки приняты")
            time.sleep(random.uniform(1, 2))
        except:
            print("Баннер куки не найден или уже принят")

        # Находим инпут и вводим email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"][placeholder="username@example.com"]'))
        )

        # Имитируем движение мыши к полю
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Кликаем на поле (фокус)
        email_input.click()
        time.sleep(random.uniform(0.5, 1))

        # Имитируем человеческий ввод с паузами
        for i, char in enumerate(email):
            email_input.send_keys(char)
            # Случайные паузы, иногда длиннее
            if i % 5 == 0 and i > 0:
                time.sleep(random.uniform(0.15, 0.3))
            else:
                time.sleep(random.uniform(0.05, 0.1))

        print(f"Email введён: {email}")

        # Долгая задержка перед нажатием кнопки (как будто читаем/проверяем)
        time.sleep(random.uniform(4, 6))

        # Имитируем движение мыши перед кликом
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Нажимаем кнопку Continue
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="test-primary-button"]'))
        )
        continue_button.click()
        print("Кнопка Continue нажата")

        # Ждём загрузки второй страницы
        time.sleep(random.uniform(2, 3))
        print("Вторая страница загружена")

        # Имитируем чтение второй страницы
        human_read_page(driver)
        time.sleep(random.uniform(1, 2))

        # Проверяем скрытые поля
        hidden_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="hidden"]')
        print(f"Найдено скрытых полей: {len(hidden_fields)}")
        for field in hidden_fields:
            name = field.get_attribute('name')
            value = field.get_attribute('value')
            if name:
                print(f"  - {name}: {value[:50] if value else 'None'}...")

        # Находим инпут для имени и вводим полное имя
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="signup-full-name-input"] input'))
        )

        # Имитируем движение мыши к полю
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Кликаем на поле (фокус)
        name_input.click()
        time.sleep(random.uniform(0.5, 1))

        # Имитируем человеческий ввод с паузами
        for i, char in enumerate(full_name):
            name_input.send_keys(char)
            # Случайные паузы, иногда длиннее
            if i % 3 == 0 and i > 0:
                time.sleep(random.uniform(0.15, 0.3))
            else:
                time.sleep(random.uniform(0.05, 0.1))

        print(f"Имя введено: {full_name}")

        # Долгая задержка перед нажатием кнопки (как будто проверяем данные)
        time.sleep(random.uniform(4, 6))

        # Имитируем движение мыши перед кликом
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Нажимаем кнопку Continue на второй странице
        continue_button_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="signup-next-button"]'))
        )
        continue_button_2.click()
        print("Кнопка Continue на второй странице нажата")

        # Дополнительная задержка (ждём загрузку третьей страницы)
        time.sleep(random.uniform(2, 3))
        print("Третья страница загружена")

        # Проверяем наличие инпута для кода верификации
        try:
            code_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="email-verification-form-code-input"] input'))
            )
            print("Инпут для кода верификации найден")
        except:
            print("ОШИБКА: Инпут для кода верификации не найден на странице!")
            # Сохраняем скриншот для отладки
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            driver.save_screenshot(f"screenshot/error_{timestamp}.png")
            print(f"Скриншот ошибки сохранён: screenshot/error_{timestamp}.png")
            return

        # Получаем код верификации из почты
        print("Получаю код верификации из почты...")
        verification_code = get_verification_code_from_email(start_time, max_attempts=2, delay=5)

        if not verification_code:
            print("ОШИБКА: Не удалось получить код верификации из почты после 2 попыток")
            # Сохраняем скриншот для отладки
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            driver.save_screenshot(f"screenshot/no_code_{timestamp}.png")
            print(f"Скриншот сохранён: screenshot/no_code_{timestamp}.png")
            return

        print(f"Код верификации получен: {verification_code}")

        # Имитируем движение мыши к полю
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Кликаем на поле (фокус)
        code_input.click()
        time.sleep(random.uniform(0.5, 1))

        # Вводим код верификации с паузами
        for i, char in enumerate(verification_code):
            code_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.2))

        print(f"Код верификации введён: {verification_code}")

        # Задержка перед нажатием кнопки
        time.sleep(random.uniform(2, 3))

        # Имитируем движение мыши перед кликом
        human_mouse_move(driver)
        time.sleep(random.uniform(1, 2))

        # Нажимаем кнопку Continue
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="email-verification-verify-button"]'))
        )
        verify_button.click()
        print("Кнопка Continue нажата (верификация)")

        # Ждём загрузку четвёртой страницы
        time.sleep(random.uniform(3, 5))
        print("Четвёртая страница загружена")

        # Дополнительная задержка
        time.sleep(random.uniform(4, 6))

        # Генерируем имя файла на основе текущей даты и времени
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = f"screenshot/{timestamp}.png"
        html_path = f"page_code/{timestamp}.html"

        # Сохраняем скриншот четвёртой страницы
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот четвёртой страницы сохранён: {screenshot_path}")

        # Получаем HTML код четвёртой страницы
        html_content = driver.page_source

        # Сохраняем HTML в файл
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML код четвёртой страницы сохранён: {html_path}")

    finally:
        # Закрываем браузер
        driver.quit()
        print("Браузер закрыт")


if __name__ == "__main__":
    main()
