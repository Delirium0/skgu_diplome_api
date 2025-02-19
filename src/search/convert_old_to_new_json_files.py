import json
import os


def convert_old_json_to_new(old_file_path, new_file_path, building_number):
    """
    Конвертирует старый формат JSON-файла в новый формат, добавляя многоязычные поля и номер здания.
    """

    try:
        with open(old_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл {old_file_path} не найден.")
        return
    except json.JSONDecodeError:
        print(f"Ошибка: Ошибка чтения JSON файла {old_file_path}.")
        return

    new_data = {
        "image_path": data["image_path"],
        "building_number": building_number,  # Укажите номер здания здесь
        "nodes": {},
        "edges": data["edges"]
    }

    for node_name, node_data in data["nodes"].items():
        x, y, node_type = node_data
        new_data["nodes"][node_name] = {
            "coords": (x, y),
            "type": node_type,
            "name": {
                "ru": "",
                "en": "",
                "kz": ""
            },
            "description": {
                "ru": "",
                "en": "",
                "kz": ""
            }
        }

    try:
        with open(new_file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        print(f"Файл {old_file_path} успешно преобразован в {new_file_path}")
    except Exception as e:
        print(f"Ошибка при записи в файл {new_file_path}: {e}")


# Пример использования:
# Укажите папку со старыми JSON файлами, новую папку и номер здания
old_files_directory = r"E:\PycharmProjects\skgu_diplome_api\src\search\old"  # Путь к папке со старыми файлами
new_files_directory = r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new"  # Путь к папке для новых файлов
building_number = "5"  # Номер здания

# Создаем новую папку, если она не существует
if not os.path.exists(new_files_directory):
    os.makedirs(new_files_directory)

# Перебираем все файлы в указанной папке
for filename in os.listdir(old_files_directory):
    if filename.endswith(".json"):
        old_file_path = os.path.join(old_files_directory, filename)
        new_file_path = os.path.join(new_files_directory, "new_" + filename)  # Добавляем префикс "new_"
        convert_old_json_to_new(old_file_path, new_file_path, building_number)
