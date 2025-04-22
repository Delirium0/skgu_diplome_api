import asyncio

from src.api.faculties.faculty_repo import faculty_repo
from src.api.faculties.schemas import FacultyCreate

repo = faculty_repo


async def add_language_literature_faculty():
    """
    Функция для тестового добавления факультета 'Институт языка и литературы'.
    Данные извлечены вручную из предоставленного HTML.
    """
    faculty_name: str = "Институт языка и литературы"

    # 1. Проверка, существует ли факультет с таким именем (хорошая практика, как в API)
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(
            f"Факультет с именем '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Создание пропущено.")
        # Возвращаем существующий факультет или None, в зависимости от того, что нужно дальше
        return existing_faculty  # или можно return None, если нужно показать, что *нового* не создано

    # 2. Заполнение данных для создания (переменная faculty_in)
    # Данные взяты из HTML страницы "Институт языка и литературы"
    faculty_in = FacultyCreate(
        name=faculty_name,
        description="Институт осуществляет подготовку специалистов высокой квалификации в области филологии, переводческого дела, казахского, русского, иностранных языков (английский, немецкий, французский) и методики их преподавания, как по программам бакалавриата, так и магистратуры. В настоящее время наши выпускники работают не только в областных и городских учреждениях образования, но и в международных организациях, базирующихся в Казахстане и за его пределами. Успешно применяют приобретенные в процессе обучения профессиональные знания, умения и навыки в трудовой деятельности.",
        history=None,  # В HTML была только ссылка на PDF-файл истории
        social_links={
            "instagram": "https://www.instagram.com/lli_nku/"  # Извлечено из HTML
        },
        building="Корпус 3",  # Извлечено из HTML
        address="г. Петропавловск, ул. Пушкина, 86",  # Извлечено из HTML
        # Телефон деканата взят из раздела "Адрес", внутренний номер добавлен из информации о директоре
        dean_phone="+7 (7152) 463491, вн. 1084"
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}'")
    # print(f"Данные: {faculty_in}") # Раскомментируй для детального просмотра объекта faculty_in

    try:
        # 3. Вызов метода репозитория для создания факультета
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)  # <--- Вот эта строка
        print("-" * 30)
        # Проверяем, что вернул репозиторий
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН!")
            print(f"ID нового факультета: {getattr(created_faculty, 'id', 'N/A')}")
            # print(f"Возвращенный объект: {created_faculty}") # Раскомментируй для просмотра всего объекта
        else:
            print("Репозиторий repo.create_faculty не вернул созданный объект.")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30)
        print(f"ПРОИЗОШЛА ОШИБКА при вызове repo.create_faculty для факультета '{faculty_in.name}':")
        import traceback
        traceback.print_exc()  # Печать полного стека ошибки для детальной отладки
        print("-" * 30)
        return None

async def add_medical_faculty():
    """
    Функция для тестового добавления факультета 'Медицинский факультет'.
    Данные извлечены вручную из предоставленного HTML.
    """
    faculty_name: str = "Медицинский факультет" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='Высшая школа медицины открыта в 2018 году. На данный момент на факультете функционируют кафедры "Фундаментальная медицина" и "Клинические дисциплины". В первый год кафедра успела вобрать в себя не только студентов по Казахстану, но и более 60 студентов из Индии. По окончанию обучения факультет подготовит специалистов бакалавриата, которые смогут осуществлять врачебную деятельность в любых медицинских учреждениях Казахстана.', # Из <div class="fac-desc">
        # В HTML ссылка на историю пустая (<a href="">), поэтому ставим None
        history=None,
        social_links={
            "instagram": "https://www.instagram.com/m_f_k_u/" # Из <div class="fac-soc">
        },
        building="УЛК", # Из <div class="fac-adr"> -> <strong>Учебный корпус: УЛК</strong>
        address="г. Петропавловск, ул. Пушкина, 86 (в)", # Из <div class="fac-adr">
        dean_phone="1190 внутренний 3019" # Из <div class="fac-adr"> -> Телефон деканата
        # Также есть телефон директора в блоке <div class="fac-dec-adr">, он совпадает
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}'")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None


async def add_agrotechnological_faculty():
    """
    Функция для тестового добавления факультета 'Агротехнологический факультет'.
    Данные извлечены вручную из предоставленного HTML.
    """
    faculty_name: str = "Агротехнологический факультет" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    # !!! Убедись, что 'repo' - это твой реальный или тестовый экземпляр репозитория !!!
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='Факультет создан 1 сентября 2018 года. Осуществляет подготовку бакалавров и магистрантов различных отраслей сельскохозяйственного производства и пищевой перерабатывающей промышленности. Выпускники факультета будут осуществлять свою деятельность в государственных учреждениях Министерства сельского хозяйства и сельскохозяйственных формированиях растениеводческого и животноводческого направлений, проектных, научно-исследовательских учреждениях, лесных хозяйствах, национальных и природных парках и заповедниках, на перерабатывающих предприятиях отраслей пищевой промышленности.', # Из <div class="fac-desc">
        history="/page/view?id=1844", # Ссылка из <div class="fac-his"><a href="...">
        social_links={
            "instagram": "https://www.instagram.com/af_nkzu/", # Из <div class="fac-soc">
            "facebook": "https://www.facebook.com/afnkzu/"  # Из <div class="fac-soc">
        },
        building="Корпус 2", # Из <div class="fac-adr">
        address="г. Петропавловск, ул. Пушкина, 86", # Из <div class="fac-adr">
        dean_phone="+7 (7152) 493202" # Из <div class="fac-adr"> -> Телефон деканата
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}'")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None

async def add_pedagogical_faculty():
    """
    Функция для тестового добавления факультета 'Педагогический факультет'.
    Данные извлечены вручную. Связанные кафедры и программы НЕ добавляются.
    """
    faculty_name: str = "Педагогический факультет" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных (только для таблицы Faculty)
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='ПФ образован в 1978 году. На факультете осуществляется обучение по восьми специальностям педагогического и творческого направлений. Педагогический факультет является центром по оказанию методической помощи учреждениям системы образования в Северо-Казахстанской области, имеет тесные связи с ведущими вузами Казахстана, России и других стран СНГ.', # Из <div class="fac-desc">
        history="/files/facultets/history/mpf.pdf", # Ссылка из <div class="fac-his"><a href="...">
        social_links={}, # В HTML секция соцсетей пуста: <div class="fac-soc">Факультет в социальных сетях: </div>
        building="Корпус 2", # Из <div class="fac-adr">
        # Адрес указан ул. Интернациональная, 26. Корпус 2 в предыдущем примере был на ул. Пушкина, 86. Уточнить, какой адрес верный для корпуса 2. Оставляем как в HTML.
        address="г. Петропавловск, ул. Интернациональная, 26", # Из <div class="fac-adr">
        dean_phone="+7 (7152) 464249" # Из <div class="fac-adr"> -> Телефон деканата
        # Списки связей оставляем пустыми (или не передаем, если схема позволяет)
        # departments=[],
        # educational_programs=[]
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}' (без связанных данных)")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None


async def add_engineering_digital_faculty():
    """
    Функция для тестового добавления факультета 'Факультет инженерии и цифровых технологий'.
    Данные извлечены вручную. Связанные кафедры и программы НЕ добавляются.
    """
    faculty_name: str = "Факультет инженерии и цифровых технологий" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных (только для таблицы Faculty)
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='Факультет инженерии и цифровых технологий динамично развивающийся факультет университета. Факультет представлен четырьмя кафедрами, которые ведут учебную и научную работу на высоком качественном уровне. Этому способствует наличие современной материальной базы и преподавателей высокой квалификации. Студенты и преподаватели факультета с гордостью выполняют миссию университета, благодаря чему факультет является центром научных идей и разработок. На выпускников факультета традиционно высокий спрос на рынке труда.', # Из <div class="fac-desc">
        history="/page/view?id=2025", # Ссылка из <div class="fac-his"><a href="...">
        social_links={
            "instagram": "https://www.instagram.com/fizt_nkzu/" # Из <div class="fac-soc">
        },
        building="Корпус 4", # Из <div class="fac-adr">
        address="г. Петропавловск, ул. Пушкина, 81", # Из <div class="fac-adr">
        dean_phone="+7 (7152) 464249" # Из <div class="fac-adr"> -> Телефон деканата
        # Списки связей оставляем пустыми
        # departments=[],
        # educational_programs=[]
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}' (без связанных данных)")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None
async def add_history_economics_law_faculty():
    """
    Функция для тестового добавления факультета 'Факультет истории, экономики и права'.
    Данные извлечены вручную. Связанные кафедры и программы НЕ добавляются.
    """
    faculty_name: str = "Факультет истории, экономики и права" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных (только для таблицы Faculty)
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='Создан в 2014 году путем слияния экономического факультета и факультета истории и права. На кафедрах факультета ведется подготовка магистров и бакалавров. Профессорско-преподавательский состав и студенты принимают активное участие в учебных, научных и общественных мероприятиях, проводимых на международном, республиканском и региональном уровнях.', # Из <div class="fac-desc">
        history="/files/facultets/history/fiep_2021.pdf", # Ссылка из <div class="fac-his"><a href="...">
        social_links={
            "instagram": "https://www.instagram.com/fiep_nku/", # Из <div class="fac-soc">
            "facebook": "https://www.facebook.com/fiepskgu.2017/" # Из <div class="fac-soc">
        },
        building="Корпус 6", # Из <div class="fac-adr">
        address="г. Петропавловск, ул. Жумабаева, 114", # Из <div class="fac-adr">
        dean_phone="+7 (7152) 461320" # Из <div class="fac-adr"> -> Телефон деканата
        # Списки связей оставляем пустыми
        # departments=[],
        # educational_programs=[]
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}' (без связанных данных)")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None



async def add_math_natural_sciences_faculty():
    """
    Функция для тестового добавления факультета 'Факультет математики и естественных наук'.
    Данные извлечены вручную. Связанные кафедры и программы НЕ добавляются.
    """
    faculty_name: str = "Факультет математики и естественных наук" # Из <h1 class="site-header-new">

    # 1. Проверка на существование
    existing_faculty = await repo.get_faculty_by_name(faculty_name)
    if existing_faculty:
        print(f"Факультет '{faculty_name}' уже существует (ID: {getattr(existing_faculty, 'id', 'N/A')}). Пропуск.")
        return existing_faculty

    # 2. Заполнение данных (только для таблицы Faculty)
    faculty_in = FacultyCreate(
        name=faculty_name,
        description='Старейший факультет нашего университета, образован как естественно-географический в 1937 г. В современном виде существует с 2018 г. Готовит учителей биологии, географии, химии, физики, математики, информатики, бакалавров химической технологии, экологии, магистров биологии, географии, химии, математики, физики, информатики, экологии, химической технологии. В 2019 г. открыта докторантура по ОП «Химическая технология органических веществ». Выпускники факультета успешно работают в школах, лицеях, сельскохозяйственных, производственных, экологических и природоохранных организациях области, Республики и зарубежных стран.', # Из <div class="fac-desc">
        history="/files/facultets/history/egf.pdf", # Ссылка из <div class="fac-his"><a href="...">
        social_links={
            "instagram": "https://www.instagram.com/fmen_skgu/" # Из <div class="fac-soc">
        },
        building="Корпус 2", # Из <div class="fac-adr">
        address="г. Петропавловск, ул. Абая, 9", # Из <div class="fac-adr">
        dean_phone="+7 (7152) 464895" # Из <div class="fac-adr"> -> Телефон деканата
        # Списки связей оставляем пустыми
        # departments=[],
        # educational_programs=[]
    )

    print(f"Подготовлены данные для создания факультета: '{faculty_in.name}' (без связанных данных)")

    try:
        # 3. Вызов репозитория
        print(f"Вызов repo.create_faculty для '{faculty_in.name}'...")
        created_faculty = await repo.create_faculty(faculty_data=faculty_in)
        print("-" * 30)
        if created_faculty:
            print(f"Факультет '{getattr(created_faculty, 'name', 'N/A')}' УСПЕШНО СОЗДАН! ID: {getattr(created_faculty, 'id', 'N/A')}")
        else:
             print(f"Факультет '{faculty_in.name}' не был создан (возможно, уже существует или ошибка в репозитории).")
        print("-" * 30)
        return created_faculty
    except Exception as e:
        print("-" * 30); print(f"ОШИБКА при создании '{faculty_in.name}':"); import traceback; traceback.print_exc(); print("-" * 30)
        return None
if __name__ == '__main__':
    asyncio.run(add_math_natural_sciences_faculty())
