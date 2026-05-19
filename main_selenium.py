import os
import time
import random
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def main():
    # URL для открытия
    target_url = "https://view.awsapps.com/start/#/device?user_code=LLHR-SPNP"

    # Email для ввода
    email = "john.smith.test2026@gmail.com"

    # Полное имя для ввода
    full_name = "Test User"

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

        # Генерируем имя файла на основе текущей даты и времени
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = f"screenshot/{timestamp}.png"
        html_path = f"page_code/{timestamp}.html"

        # Сохраняем скриншот третьей страницы
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот третьей страницы сохранён: {screenshot_path}")

        # Получаем HTML код третьей страницы
        html_content = driver.page_source

        # Сохраняем HTML в файл
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML код третьей страницы сохранён: {html_path}")

    finally:
        # Закрываем браузер
        driver.quit()
        print("Браузер закрыт")


if __name__ == "__main__":
    main()
