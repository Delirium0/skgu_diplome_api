import chardet
import requests
from requests_ntlm import HttpNtlmAuth


async def skgu_login(login: str, password: str, user_id: int) -> bool:
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year=2023&Semester=0&IDStudent={user_id}&iFlagStudent=1'

    domain = ''
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + login, password)

    response = session.get(url)
    # Определение кодировки текста с помощью chardet
    encoding = chardet.detect(response.content)['encoding']

    try:
        decoded_content = response.content.decode(encoding)
        if '<div id="header"><h1>Ошибка сервера в приложении "DEFAULT WEB SITE"</h1></div>' in decoded_content:
            return False
        return True
    except Exception as e:
        print(e)

