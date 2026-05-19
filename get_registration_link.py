import requests
import json


def get_aws_registration_link():
    """Получает ссылку регистрации AWS от omniroute"""

    # Omniroute API endpoint
    url = "http://localhost:3000/api/oauth/kiro/device-code"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Извлекаем данные
        verification_uri = data.get('verification_uri_complete') or data.get('verificationUriComplete')
        device_code = data.get('device_code') or data.get('deviceCode')
        user_code = data.get('user_code') or data.get('userCode')

        return {
            'url': verification_uri,
            'device_code': device_code,
            'user_code': user_code,
            'expires_in': data.get('expires_in', data.get('expiresIn')),
            'interval': data.get('interval', 5)
        }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к omniroute: {e}")
        return None


if __name__ == "__main__":
    link_data = get_aws_registration_link()
    if link_data:
        print(json.dumps(link_data, indent=2))
    else:
        print("Не удалось получить ссылку регистрации")
