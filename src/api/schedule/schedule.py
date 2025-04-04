import datetime
import re

from bs4 import BeautifulSoup


def parse_row(row):
    data = {}
    cols = row.find_all('td')

    data['День недели'] = cols[0].find('p', class_='sum').text.strip()
    data['Дата'] = cols[0].find('div', class_='cll').text.strip().split()[0] if cols[0].find('div',
                                                                                             class_='cll') else None

    date_div = cols[0].find('div', class_='cll')
    if date_div:
        data['Дата'] = date_div.find(text=True, recursive=False).strip()
    else:
        data['Дата'] = None

    data['Факультет'] = cols[1].text.strip()
    data['Кафедра'] = cols[2].text.strip()

    # Извлекаем номер пары и время из одной ячейки
    para_time_cell = cols[3]
    para_text = para_time_cell.find(text=True, recursive=False).strip() if para_time_cell else ""

    para_num = para_text.split()[0] if para_text else None
    time_match = re.search(r'(\d+\.\d+)\s*-\s*(\d+\.\d+)', para_text)
    data['Пара'] = para_num
    # Находим первый <td> с классом cll
    td = cols[3].find('div')
    # Извлекаем текст времени
    if td:
        # Используем .string для извлечения текста из первого уровня вложенности
        top_level_text = td.string.strip() if td.string else td.text.strip()

        # Извлекаем из текста время с помощью регулярного выражения
        time_match = re.search(r'\d{1,2}\.\d{2} - \d{1,2}\.\d{2}', top_level_text)
        if time_match:
            time = time_match.group()
            data['Время'] = time

    data['Группа'] = cols[5].text.strip()

    data['Курс'] = cols[6].text.strip()

    data['Дисциплина'] = cols[7].text.strip()
    data['Тип занятия'] = cols[8].text.strip()

    # Извлекаем информацию о преподавателе, должности и степени
    teacher_cell = cols[9]
    teacher_name = teacher_cell.text.split('(')[0].strip()
    degree_title = teacher_cell.find_all('div', class_='gr')  # находим все дивы с классом 'gr'
    title = degree_title[0].text.strip() if degree_title else ""  # если есть должность, то извлекаем
    degree = degree_title[1].text.strip() if len(degree_title) > 1 else ""  # если есть ученая степень, то извлекаем

    data['Преподаватель'] = teacher_name
    # data['Должность'] = title  # добавляем должность
    # data['Ученая степень'] = degree  # добавляем ученую степень

    data['Аудитория'] = cols[10].text.strip()

    return data


def parse_schedule_from_page(html_data):
    soup = BeautifulSoup(html_data, 'lxml')
    table = soup.find('table', border='1')

    if not table:
        return None

    rows = table.find_all('tr')[1:]
    schedule = []  # Возвращаем список словарей, а не словарь словарей
    for row in rows:
        try:
            row_data = parse_row(row)
            schedule.append(row_data)
        except Exception as e:
            print(f"Error parsing row: {e}")

    return schedule


def get_current_lesson(schedule_data):
    """
    Возвращает информацию о текущем уроке на основе текущего времени и расписания.

    Args:
        schedule_data: Список словарей, представляющих расписание.

    Returns:
        Словарь с информацией о текущем уроке (преподаватель, время, название предмета, аудитория)
        или None, если текущего урока нет.
    """
    now = datetime.datetime.now()
    current_weekday = now.strftime("%A").upper()  # Получаем текущий день недели в верхнем регистре
    current_time = now.time()

    weekday_mapping = {
        "MONDAY": "ПОНЕДЕЛЬНИК",
        "TUESDAY": "ВТОРНИК",
        "WEDNESDAY": "СРЕДА",
        "THURSDAY": "ЧЕТВЕРГ",
        "FRIDAY": "ПЯТНИЦА",
        "SATURDAY": "СУББОТА",
        "SUNDAY": "ВОСКРЕСЕНЬЕ",
    }

    current_weekday_rus = weekday_mapping.get(current_weekday)  # Переводим на русский

    for lesson in schedule_data['results']:
        if lesson['День недели'] == current_weekday_rus:  # Сравниваем с русским названием дня недели
            start_time_str = lesson['Время'].split(" - ")[0]
            end_time_str = lesson['Время'].split(" - ")[1]

            try:
                start_time = datetime.datetime.strptime(start_time_str, "%H.%M").time()
                end_time = datetime.datetime.strptime(end_time_str, "%H.%M").time()

                if start_time <= current_time <= end_time:
                    return {
                        "Преподаватель": lesson['Преподаватель'],
                        "Время": lesson['Время'],
                        "Дисциплина": lesson['Дисциплина'],
                        "Аудитория": lesson['Аудитория'],
                    }
            except ValueError:
                print(f"Ошибка формата времени в записи: {lesson['Время']}")
                return None  # Или другое действие при ошибке

    return None  # Если текущий урок не найден
