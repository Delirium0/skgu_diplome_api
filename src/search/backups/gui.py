import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import json
import heapq
from collections import deque

# Глобальные переменные
image_path = None
image = None
image_tk = None
nodes = {}  # {'node_name': {'coords': (x, y), 'type': type, 'name': {'ru':.., 'en': ...}, 'description':{...}}}
edges = []  # [(node1, node2, weight)]
current_mode = "add_node"
start_node = None
end_node = None
graph = {}
DEFAULT_NODE_TYPE = "corridor"
DEFAULT_LANGUAGE = "ru"  # Язык по умолчанию
building_number = ""  # Номер здания

# Функции алгоритмов поиска пути (остаются без изменений)
def bfs_path(graph, start, goal):
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        if current not in graph:
            continue  # Проверка наличия узла в графе
        for neighbor, _ in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def dijkstra_path(graph, start, goal):
    if start not in graph or goal not in graph:
        return None  # Проверка наличия узла в графе
    queue = [(0, start, [start])]
    seen = {start: 0}
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == goal:
            return path
        if node not in graph:
            continue  # Проверка наличия узла в графе
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if neighbor not in seen or new_cost < seen[neighbor]:
                seen[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
    return None

# Функции отрисовки (нужно немного изменить)
def draw_nodes_and_edges(img):
    draw = ImageDraw.Draw(img)
    for node_name, node_data in nodes.items():
        x, y = node_data['coords']
        node_type = node_data['type']  # Используем тип узла
        r = 5
        draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
        draw.text((x + 5, y - 5), node_name, fill='blue')

    for node1, node2, weight in edges:
        if node1 in nodes and node2 in nodes:
            x1, y1 = nodes[node1]['coords']
            x2, y2 = nodes[node2]['coords']
            draw.line((x1, y1, x2, y2), fill='black', width=2)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            draw.text((mid_x, mid_y), str(weight), fill='black')

    return img


def draw_path(img, path):
    if not path:
        return img
    draw = ImageDraw.Draw(img)
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        if node1 in nodes and node2 in nodes:
            x1, y1 = nodes[node1]['coords']
            x2, y2 = nodes[node2]['coords']
            draw.line((x1, y1, x2, y2), fill='red', width=3)
    return img

# Функции обработки событий
def load_image():
    global image_path, image, image_tk
    image_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg")])
    if image_path:
        image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        canvas.config(width=image.width, height=image.height)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        redraw_image()


def add_node_click(event):
    global image
    if current_mode == "add_node":
        x, y = event.x, event.y
        add_node(x, y)


def add_node(x, y):
    global image, image_tk, building_number
    node_name = entry_node_name.get()
    node_type = combo_node_type.get()
    name_ru = entry_name_ru.get()
    name_en = entry_name_en.get()
    name_kz = entry_name_kz.get()  # Добавлено поле для казахского
    description_ru = entry_description_ru.get()
    description_en = entry_description_en.get()
    description_kz = entry_description_kz.get()  # Добавлено поле для казахского

    if not node_name:
        messagebox.showerror("Ошибка", "Введите имя узла")
        return
    if node_name in nodes:
        messagebox.showerror("Ошибка", "Узел с таким именем уже существует")
        return

    nodes[node_name] = {
        'coords': (x, y),
        'type': node_type,
        'name': {
            'ru': name_ru,
            'en': name_en,
            'kz': name_kz,  # Сохраняем казахское название
        },
        'description': {
            'ru': description_ru,
            'en': description_en,
            'kz': description_kz  # Сохраняем казахское описание
        }
    }

    entry_node_name.delete(0, tk.END)
    entry_name_ru.delete(0, tk.END)
    entry_name_en.delete(0, tk.END)
    entry_name_kz.delete(0, tk.END)  # Очищаем поле казахского названия
    entry_description_ru.delete(0, tk.END)
    entry_description_en.delete(0, tk.END)
    entry_description_kz.delete(0, tk.END)  # Очищаем поле казахского описания
    redraw_image()


def add_edge():
    node1 = entry_edge_node1.get()
    node2 = entry_edge_node2.get()
    weight_str = entry_edge_weight.get()

    if not (node1 and node2 and weight_str):
        messagebox.showerror("Ошибка", "Введите имена узлов и вес ребра")
        return

    if node1 not in nodes or node2 not in nodes:
        messagebox.showerror("Ошибка", "Один или оба узла не существуют")
        return

    try:
        weight = float(weight_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный вес ребра")
        return

    edges.append((node1, node2, weight))
    entry_edge_node1.delete(0, tk.END)
    entry_edge_node2.delete(0, tk.END)
    entry_edge_weight.delete(0, tk.END)
    redraw_image()


def build_graph():
    global graph
    graph = {}
    for node_name in nodes:
        graph[node_name] = []
    for node1, node2, weight in edges:
        graph[node1].append((node2, weight))
        graph[node2].append((node1, weight))


def find_path():
    global start_node, end_node
    start_node = entry_start_node.get()
    end_node = entry_end_node.get()

    if not (start_node and end_node):
        messagebox.showerror("Ошибка", "Введите начальный и конечный узлы")
        return

    if start_node not in nodes or end_node not in nodes:
        messagebox.showerror("Ошибка", "Один или оба узла не существуют")
        return

    build_graph()

    path = dijkstra_path(graph, start_node, end_node)
    if path:
        print("Найденный путь:", path)
    else:
        print("Путь не найден.")

    redraw_image(path)


def redraw_image(path=None):
    global image, image_tk
    if image:
        img_copy = image.copy()
        img_copy = draw_nodes_and_edges(img_copy)
        if path:
            img_copy = draw_path(img_copy, path)
        image_tk = ImageTk.PhotoImage(img_copy)
        canvas.itemconfig(image_on_canvas, image=image_tk)

def set_building_number():
    global building_number
    building_number = entry_building_number.get()
    if not building_number:
        messagebox.showerror("Ошибка", "Введите номер здания")
        return

def save_data():
    global building_number
    data = {
        "image_path": image_path,
        "building_number": building_number,
        "nodes": nodes,  # Сохраняем структуру узла полностью
        "edges": edges
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def load_data():
    global image_path, image, image_tk, nodes, edges, building_number
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                image_path = data["image_path"]
                nodes = data["nodes"]
                edges = data["edges"]
                building_number = data.get("building_number", "")  # Загружаем номер здания

                # Обновляем поле ввода номера здания, если он есть в данных
                entry_building_number.delete(0, tk.END)
                entry_building_number.insert(0, building_number)

                image = Image.open(image_path)
                image_tk = ImageTk.PhotoImage(image)
                canvas.config(width=image.width, height=image.height)
                canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
                redraw_image()

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл не найден.")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Ошибка чтения JSON файла.")

# GUI
root = tk.Tk()
root.title("Редактор графа для поиска пути")

# Элементы управления
frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.TOP, fill=tk.X)

button_load_image = tk.Button(frame_controls, text="Загрузить изображение", command=load_image)
button_load_image.pack(side=tk.LEFT, padx=5, pady=5)

button_save_data = tk.Button(frame_controls, text="Сохранить граф", command=save_data)
button_save_data.pack(side=tk.LEFT, padx=5, pady=5)

button_load_data = tk.Button(frame_controls, text="Загрузить граф", command=load_data)
button_load_data.pack(side=tk.LEFT, padx=5, pady=5)

# Номер здания
frame_building_number = tk.Frame(root)
frame_building_number.pack(side=tk.TOP, fill=tk.X)

label_building_number = tk.Label(frame_building_number, text="Номер здания:")
label_building_number.pack(side=tk.LEFT, padx=5, pady=5)

entry_building_number = tk.Entry(frame_building_number)
entry_building_number.pack(side=tk.LEFT, padx=5, pady=5)

button_set_building = tk.Button(frame_building_number, text="Установить номер здания", command=set_building_number)
button_set_building.pack(side=tk.LEFT, padx=5, pady=5)



# Добавление узла
frame_add_node = tk.Frame(root)
frame_add_node.pack(side=tk.TOP, fill=tk.X)

label_node_name = tk.Label(frame_add_node, text="Имя узла:")
label_node_name.pack(side=tk.LEFT, padx=5, pady=5)

entry_node_name = tk.Entry(frame_add_node)
entry_node_name.pack(side=tk.LEFT, padx=5, pady=5)

label_node_type = tk.Label(frame_add_node, text="Тип узла:")
label_node_type.pack(side=tk.LEFT, padx=5, pady=5)

node_types = ["corridor", "office", "stairs", "entrance", "toilet", "other"]
combo_node_type = tk.ttk.Combobox(frame_add_node, values=node_types)
combo_node_type.set(DEFAULT_NODE_TYPE)
combo_node_type.pack(side=tk.LEFT, padx=5, pady=5)

# Многоязычные поля
label_name_ru = tk.Label(frame_add_node, text="Название (русский):")
label_name_ru.pack(side=tk.LEFT, padx=5, pady=5)
entry_name_ru = tk.Entry(frame_add_node)
entry_name_ru.pack(side=tk.LEFT, padx=5, pady=5)

label_description_ru = tk.Label(frame_add_node, text="Описание (русский):")
label_description_ru.pack(side=tk.LEFT, padx=5, pady=5)
entry_description_ru = tk.Entry(frame_add_node)
entry_description_ru.pack(side=tk.LEFT, padx=5, pady=5)

label_name_en = tk.Label(frame_add_node, text="Название (английский):")
label_name_en.pack(side=tk.LEFT, padx=5, pady=5)
entry_name_en = tk.Entry(frame_add_node)
entry_name_en.pack(side=tk.LEFT, padx=5, pady=5)

label_description_en = tk.Label(frame_add_node, text="Описание (английский):")
label_description_en.pack(side=tk.LEFT, padx=5, pady=5)
entry_description_en = tk.Entry(frame_add_node)
entry_description_en.pack(side=tk.LEFT, padx=5, pady=5)

# Добавляем поля для казахского языка
label_name_kz = tk.Label(frame_add_node, text="Название (казахский):")
label_name_kz.pack(side=tk.LEFT, padx=5, pady=5)
entry_name_kz = tk.Entry(frame_add_node)
entry_name_kz.pack(side=tk.LEFT, padx=5, pady=5)

label_description_kz = tk.Label(frame_add_node, text="Описание (казахский):")
label_description_kz.pack(side=tk.LEFT, padx=5, pady=5)
entry_description_kz = tk.Entry(frame_add_node)
entry_description_kz.pack(side=tk.LEFT, padx=5, pady=5)


# Добавление ребра
frame_add_edge = tk.Frame(root)
frame_add_edge.pack(side=tk.TOP, fill=tk.X)

label_edge_node1 = tk.Label(frame_add_edge, text="Узел 1:")
label_edge_node1.pack(side=tk.LEFT, padx=5, pady=5)
entry_edge_node1 = tk.Entry(frame_add_edge)
entry_edge_node1.pack(side=tk.LEFT, padx=5, pady=5)

label_edge_node2 = tk.Label(frame_add_edge, text="Узел 2:")
label_edge_node2.pack(side=tk.LEFT, padx=5, pady=5)
entry_edge_node2 = tk.Entry(frame_add_edge)
entry_edge_node2.pack(side=tk.LEFT, padx=5, pady=5)

label_edge_weight = tk.Label(frame_add_edge, text="Вес ребра:")
label_edge_weight.pack(side=tk.LEFT, padx=5, pady=5)
entry_edge_weight = tk.Entry(frame_add_edge)
entry_edge_weight.pack(side=tk.LEFT, padx=5, pady=5)

button_add_edge = tk.Button(frame_add_edge, text="Добавить ребро", command=add_edge)
button_add_edge.pack(side=tk.LEFT, padx=5, pady=5)

# Поиск пути
frame_find_path = tk.Frame(root)
frame_find_path.pack(side=tk.TOP, fill=tk.X)

label_start_node = tk.Label(frame_find_path, text="Начальный узел:")
label_start_node.pack(side=tk.LEFT, padx=5, pady=5)
entry_start_node = tk.Entry(frame_find_path)
entry_start_node.pack(side=tk.LEFT, padx=5, pady=5)

label_end_node = tk.Label(frame_find_path, text="Конечный узел:")
label_end_node.pack(side=tk.LEFT, padx=5, pady=5)
entry_end_node = tk.Entry(frame_find_path)
entry_end_node.pack(side=tk.LEFT, padx=5, pady=5)

button_find_path = tk.Button(frame_find_path, text="Построить маршрут", command=find_path)
button_find_path.pack(side=tk.LEFT, padx=5, pady=5)

# Канва для отображения изображения
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
canvas.bind("<Button-1>", add_node_click)

image_on_canvas = canvas.create_image(0, 0, anchor=tk.NW)

# Стили
style = ttk.Style()
style.configure("TButton", padding=5, relief="raised")
style.configure("TCombobox", padding=5)

root.mainloop()