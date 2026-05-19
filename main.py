import os
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright


def main():
    # URL для открытия
    target_url = "https://view.awsapps.com/start/#/device?user_code=LLHR-SPNP"

    # Email для ввода (используем новый, незарегистрированный)
    email = "test.automation.2026@scriptium.uk"

    # Полное имя для ввода
    full_name = "Test User"

    # Создаём папки если их нет
    os.makedirs("screenshot", exist_ok=True)
    os.makedirs("page_code", exist_ok=True)

    print(f"Открываю страницу: {target_url}")

    with sync_playwright() as p:
        # Запускаем браузер в headless режиме с дополнительными аргументами
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )

        # Создаём новый контекст с реалистичными параметрами и антидетекцией
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
        )

        # Открываем новую страницу
        page = context.new_page()

        # Добавляем логирование сетевых запросов
        def log_request(request):
            if 'api' in request.url or 'signup' in request.url.lower():
                print(f"→ REQUEST: {request.method} {request.url}")

        def log_response(response):
            if 'api' in response.url or 'signup' in response.url.lower():
                print(f"← RESPONSE: {response.status} {response.url}")
                # Логируем тело ответа для ошибок
                if response.status >= 400:
                    try:
                        body = response.text()
                        print(f"   ERROR BODY: {body[:500]}")
                    except:
                        pass

        page.on("request", log_request)
        page.on("response", log_response)

        # Добавляем скрипт для маскировки автоматизации
        page.add_init_script("""
            // Переопределяем navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Добавляем Chrome runtime
            window.chrome = {
                runtime: {}
            };

            // Переопределяем permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Добавляем плагины
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Добавляем языки
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # Переходим по URL и ждём полной загрузки
        page.goto(target_url, wait_until="networkidle")

        print("Страница загружена")

        # Дополнительная задержка
        time.sleep(random.uniform(2, 4))

        # Принимаем куки если баннер есть
        try:
            accept_cookies = page.locator('button[data-id="awsccc-cb-btn-accept"]')
            if accept_cookies.is_visible(timeout=2000):
                accept_cookies.click()
                print("Куки приняты")
                time.sleep(random.uniform(1, 2))
        except:
            print("Баннер куки не найден или уже принят")

        # Находим инпут и вводим email
        email_input = page.locator('input[type="text"][placeholder="username@example.com"]')
        email_input.fill(email)
        print(f"Email введён: {email}")

        # Случайная задержка перед нажатием кнопки
        time.sleep(random.uniform(1, 2))

        # Нажимаем кнопку Continue
        continue_button = page.locator('button[data-testid="test-primary-button"]')
        continue_button.click()
        print("Кнопка Continue нажата")

        # Ждём загрузки второй страницы
        page.wait_for_load_state("networkidle")
        print("Вторая страница загружена")

        # Дополнительная задержка
        time.sleep(random.uniform(3, 5))

        # Проверяем скрытые поля формы на второй странице
        hidden_fields = page.locator('input[type="hidden"]').all()
        print(f"Найдено скрытых полей: {len(hidden_fields)}")
        for field in hidden_fields:
            name = field.get_attribute('name')
            value = field.get_attribute('value')
            if name:
                print(f"  - {name}: {value[:50] if value else 'None'}...")

        # Находим инпут для имени и вводим полное имя
        name_input = page.locator('[data-testid="signup-full-name-input"] input')
        name_input.fill(full_name)
        print(f"Имя введено: {full_name}")

        # Случайная задержка перед нажатием кнопки
        time.sleep(random.uniform(1, 2))

        # Нажимаем кнопку Continue на второй странице
        continue_button_2 = page.locator('button[data-testid="signup-next-button"]')
        continue_button_2.click()
        print("Кнопка Continue на второй странице нажата")

        # Дополнительная задержка (ждём загрузку третьей страницы)
        time.sleep(random.uniform(4, 6))
        print("Третья страница загружена")

        # Генерируем имя файла на основе текущей даты и времени
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = f"screenshot/{timestamp}.png"
        html_path = f"page_code/{timestamp}.html"

        # Сохраняем скриншот третьей страницы
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Скриншот третьей страницы сохранён: {screenshot_path}")

        # Получаем HTML код третьей страницы
        html_content = page.content()

        # Сохраняем HTML в файл
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML код третьей страницы сохранён: {html_path}")

        # Закрываем браузер
        browser.close()
        print("Браузер закрыт")


if __name__ == "__main__":
    main()
