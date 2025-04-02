from bs4 import BeautifulSoup


async def parsing_evaluations(content: str) -> list | None:
    soup = BeautifulSoup(content, 'lxml')
    td_element = soup.find('td', string=lambda text: text and 'НЕТ ДАННЫХ!!!' in text.strip())
    if td_element:
        print("Найдено td, содержащий 'НЕТ ДАННЫХ!!!'")
        return None
    table = soup.find('table', attrs={'cellpadding': '2'})
    rows = table.find_all('tr')
    evaluations_result = []
    for i in range(1, len(rows)):
        tds = rows[i].find_all('td')
        td_text = tds[0].get_text(strip=True)
        div_element = tds[0].find('div', class_='gr')
        if div_element:
            # Получаем текст из элемента <div>
            div_text = div_element.get_text(strip=True)

            # Разбиваем текст из <div> на части, используя ';'
            parts = div_text.split(';')

            # Извлекаем информацию о преподавателе и названии предмета
            subject = td_text.replace(div_text, '').strip()  # Название предмета
            teacher_info = parts[1].strip()  # Информация о преподавателе

        else:
            subject = None
            teacher_info = None
        result_dict = {
            'subject_name': subject,
            'teacher': teacher_info,
            '1': tds[1].text if len(tds) > 1 else '',  # Извлекаем текст из tds[1], если он существует
            '2': tds[2].text if len(tds) > 2 else '',  # Извлекаем текст из tds[2], если он существует
            '3': tds[3].text if len(tds) > 3 else '',  # Извлекаем текст из tds[3], если он существует
            '4': tds[4].text if len(tds) > 4 else '',  # Извлекаем текст из tds[4], если он существует
            '5': tds[5].text if len(tds) > 5 else '',  # Извлекаем текст из tds[5], если он существует
            '6': tds[6].text if len(tds) > 6 else '',  # Извлекаем текст из tds[6], если он существует
            '7': tds[7].text if len(tds) > 7 else '',  # Извлекаем текст из tds[7], если он существует
            '8': tds[8].text if len(tds) > 8 else '',  # Извлекаем текст из tds[8], если он существует
            '9': tds[9].text if len(tds) > 9 else '',  # Извлекаем текст из tds[9], если он существует
            '10': tds[10].text if len(tds) > 10 else '',  # Извлекаем текст из tds[10], если он существует
            '11': tds[11].text if len(tds) > 11 else '',  # Извлекаем текст из tds[11], если он существует
            '12': tds[12].text if len(tds) > 12 else '',  # Извлекаем текст из tds[12], если он существует
            '13': tds[13].text if len(tds) > 13 else '',  # Извлекаем текст из tds[13], если он существует
            '14': tds[14].text if len(tds) > 14 else '',  # Извлекаем текст из tds[14], если он существует
            '15': tds[15].text if len(tds) > 15 else '',  # Извлекаем текст из tds[15], если он существует
            "average_grade": tds[16].text.strip() if len(tds) > 16 else ''
        }
        evaluations_result.append(result_dict)
    return evaluations_result


async def parsing_user_id(content: str) -> dict:
    soup = BeautifulSoup(content, 'lxml')
    select = soup.find('select', id='cmbStudent')
    if select:
        options = select.find_all("option")
        last_option_value = options[-1]["value"]  # значение последнего option
        return last_option_value


async def parsing_rating_group(content: str) -> list:
    soup = BeautifulSoup(content, 'lxml')

    table = soup.find('table', attrs={'cellpadding': '2'})
    trs = table.find_all('tr')

    main_table = soup.find('table').find_all('tr')[1].find('td').find('table').find_all('tr')[0].find('td').find(
        'table').find_all('tr')

    subject_dict = {}

    for subject in main_table:
        td_element = subject.find('td', class_='tea')

        # Извлечение текста до первого встреченного тега <b>
        subject_name = ''
        for item in td_element.contents:
            if item.name == 'b':
                break
            subject_name += str(item)

        # Очистка полученного текста от лишних пробелов и переносов строк
        subject_name = subject_name.strip()

        # Извлечение числа из строки (например, '1)')
        number = subject_name.split(')')[0].strip('(')

        # Удаление числа и лишних пробелов из названия предмета
        subject_title = subject_name.split(')')[1].strip()

        # Удаление строки (Экзамен) из названия предмета
        subject_title = subject_title.replace('(Экзамен', '').strip()

        # Запись в словарь: ключ - число, значение - название предмета без числа и (Экзамен)
        subject_dict[number] = subject_title

    group_rating = []
    for i in range(1, len(trs) - 1):
        tds = trs[i].find_all('td')
        # print('-______________')
        # for e in range(len(tds)):
        #     print(tds[e], print(e))
        result_dict = {
            'place': tds[0].text,
            'name': tds[1].text,
            f'{subject_dict["1"]}': tds[3].text,
            f'{subject_dict["2"]}': tds[4].text,
            f'{subject_dict["3"]}': tds[5].text,
            f'{subject_dict["4"]}': tds[6].text,
            f'{subject_dict["5"]}': tds[7].text,
            'average_score': tds[8].text,

        }
        group_rating.append(result_dict)

    return group_rating
