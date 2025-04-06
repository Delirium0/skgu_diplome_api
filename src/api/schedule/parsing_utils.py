from typing import Dict, List

from bs4 import BeautifulSoup


async def create_schedule_url_fstring_unsafe(base_url: str, selected_options: dict) -> str:
    """
    Создает URL с помощью f-string (БЕЗ URL-КОДИРОВАНИЯ - ОПАСНО!).
    Использовать только если уверены в безопасности значений параметров.
    """
    return (
        f"{base_url}?"
        f"Opera=4"
        f"&Faculty={selected_options.get('cmbFaculties', '0')}"
        f"&EduForm={selected_options.get('cmbEduForms', '0')}"
        f"&Group={selected_options.get('cmbGroup', '0')}"
        f"&Chair={selected_options.get('cmbChairs', '0')}"
        f"&Year={selected_options.get('cmbYear', '0')}"
        f"&Semester={selected_options.get('cmbSemester', '0')}"
        f"&Period={selected_options.get('cmbPeriod', '0')}"
        f"&Curs={selected_options.get('cmbCurs', '0')}"
        f"&isLangRu={selected_options.get('cmbisLangRu', '0')}"
        f"&IDTeacher={selected_options.get('cmbTeacher', '0')}"
        f"&Speciality={selected_options.get('cmbSpeciality', '0')}"
    )


# Пример использования (с теми же parsed_params):

async def parser_student_info_schedule_from_html(html_data):
    soup = BeautifulSoup(html_data, 'lxml')

    selected_options = {}
    select_elements = soup.find_all('select')

    for select in select_elements:
        select_name = select.get('name')
        if not select_name:  # Если вдруг у select нет атрибута name, пропускаем
            continue

        selected_option = select.find('option', selected=True)
        if selected_option:
            selected_value = selected_option.get('value')  # Извлекаем value атрибут
            selected_options[select_name] = selected_value
    return selected_options


async def parse_student_info_from_html(html_data):
    """
    Извлекает информацию о текущем выборе учебного года, семестра и ID студента из HTML.

    Args:
        html_data: Строка, содержащая HTML-код страницы с формой выбора.

    Returns:
        Словарь с ключами 'year', 'semester', 'student_id' и соответствующими значениями,
        или None, если не удалось извлечь какую-либо информацию.
    """
    soup = BeautifulSoup(html_data, 'lxml')
    student_info = {}

    # Извлекаем учебный год
    year_select = soup.find('select', id='cmbYear')
    if year_select:
        selected_year_option = year_select.find('option', selected=True)
        if selected_year_option:
            student_info['year'] = selected_year_option['value']
        else:
            student_info['year'] = None  # Если selected не найден, но select есть
    else:
        return None  # Если select 'cmbYear' не найден, значит структура страницы не соответствует ожиданиям

    # Извлекаем семестр
    semester_select = soup.find('select', id='cmbSemester')
    if semester_select:
        selected_semester_option = semester_select.find('option', selected=True)
        if selected_semester_option:
            student_info['semester'] = selected_semester_option['value']
        else:
            student_info['semester'] = None  # Если selected не найден, но select есть
    else:
        return None  # Если select 'cmbSemester' не найден

    # Извлекаем ID студента
    student_select = soup.find('select', id='cmbStudent')
    if student_select:
        selected_student_option = student_select.find('option', selected=True)
        if selected_student_option:
            student_info['student_id'] = selected_student_option['value']
        else:
            student_info['student_id'] = None  # Если selected не найден, но select есть
    else:
        return None  # Если select 'cmbStudent' не найден

    return student_info


async def parse_exams_table(html_content: str) -> List[Dict[str, Dict]]:
    """
    Parses the HTML content of a table and extracts exam evaluations into a list of dictionaries.

    Args:
        html_content: The HTML content of the table as a string.

    Returns:
        A list of dictionaries, where each dictionary represents a subject.
        The key of the main dictionary is the "Название дисциплины" (Discipline Name),
        and the value is a dictionary containing all other fields as key-value pairs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='table table-hover table-condensed table-bordered')
    if not table:
        return []

    exams_data: List[Dict[str, Dict]] = []
    rows = table.find('tbody').find_all('tr')

    header_row = table.find('thead').find('tr')
    headers = [th.text.strip() for th in header_row.find_all('th')]

    for row in rows:
        if row.find('th'):  # skip header row if accidentally included in tbody
            continue
        if row.find('td', colspan="11"):  # skip GPA row
            continue
        if 'bg-danger' in row.get('class', []):  # skip rows with bg-danger class
            continue

        cells = row.find_all('td')
        if not cells:
            continue

        discipline_name_cell = cells[2]
        discipline_name = discipline_name_cell.text.strip()

        exam_info: Dict[str, str] = {}
        for i in range(len(headers)):
            if headers[i] == 'Название дисциплины':
                continue  # Discipline name is the main key

            cell_value = cells[i].text.strip()
            exam_info[headers[i]] = cell_value

        exams_data_entry: Dict[str, Dict] = {}
        exams_data_entry[discipline_name] = exam_info
        exams_data.append(exams_data_entry)

    return exams_data


async def auth_check(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)
