from collections import deque

import tkinter as tk
from tkinter import font, ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random


def process_tram_file(file_path):
    """
    Обробка файлу з інформацією про трамвайні маршрути

    file_path - шлях до файлу з інформацією про трамвайні маршрути
    повертає: словник з інформацією про трамвайні маршрути
    """
    trams = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_tram = None
    current_route_name = None
    direct_route = []
    reverse_route = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect new tram number
        if line and line[0].isdigit():
            if current_tram:
                # Save previous tram route before processing new tram
                trams[current_tram] = [current_route_name, direct_route, reverse_route,
                                       set(direct_route + reverse_route)]

            # Parse tram number
            current_tram = int(line.strip())
            i += 1
            current_route_name = lines[i].strip()
            direct_route = []
            reverse_route = []

        # Parse the direct route
        elif "Прямий напрямок:" in line:
            direct_route = line.split("Прямий напрямок:")[1].split(" - ")

        # Parse the reverse route
        elif "Зворотній напрямок:" in line:
            reverse_route = line.split("Зворотній напрямок:")[1].split(" - ")

        i += 1

    # Save the last tram's route
    if current_tram:
        trams[current_tram] = [current_route_name, direct_route, reverse_route, set(direct_route + reverse_route)]

    return trams


trams = process_tram_file('TramsInfo.txt')


def find_trams_by_stop(tram_routes, stop_name):
    """
        Пошук трамваїв, які зупиняються на заданій зупинці

        tram_routes - словник з інформацією про трамвайні маршрути
        stop_name - назва зупинки
        повертає: список номерів трамваїв, які зупиняються на заданій зупинці
        """
    trams = []
    for tram, routes in tram_routes.items():
        if stop_name in routes[1] or stop_name in routes[2]:
            trams.append(tram)
    return trams


def find_best_route(tram_routes, start_stop, end_stop):
    """
        Пошук найкращого маршруту між двома зупинками

        tram_routes - словник з інформацією про трамвайні маршрути
        start_stop - назва початкової зупинки
        end_stop - назва кінцевої зупинки
        повертає: список кортежів з інформацією про маршрут (номер трамваю, список зупинок, кількість зупинок)
        """
    queue = deque([(start_stop, [], 0)])  # (current_stop, path, transfers)
    visited = set()

    while queue:
        current_stop, path, transfers = queue.popleft()

        if current_stop == end_stop:
            return path

        if (current_stop, transfers) in visited:
            continue

        visited.add((current_stop, transfers))

        for tram, routes in tram_routes.items():
            for direction in [1, 2]:
                if current_stop in routes[direction]:
                    start_index = routes[direction].index(current_stop)
                    for next_stop in routes[direction][start_index:]:
                        if next_stop == end_stop:
                            return path + [(tram, routes[direction][start_index:routes[direction].index(next_stop) + 1],
                                            routes[direction].index(next_stop) - start_index)]
                        if (next_stop, transfers + 1) not in visited:
                            queue.append((next_stop, path + [(tram, routes[direction][
                                                                    start_index:routes[direction].index(next_stop) + 1],
                                                              routes[direction].index(next_stop) - start_index)],
                                          transfers + 1))

    return None


def create_route_text(tram_routes, start_stop, end_stop):
    route = find_best_route(tram_routes, start_stop, end_stop)
    if not route:
        return "Маршрут не знайдено. Перевірте коректність введених назв зупинок."

    route_text = []
    for i, (tram, stops, count) in enumerate(route):
        if count == 1:
            stop_text = "проїдьте 1 зупинку"
        elif count in [2, 3, 4]:
            stop_text = f"проїдьте {count} зупинки"
        else:
            stop_text = f"проїдьте {count} зупинок"

        if i == 0:
            route_text.append(f"Скористайтеся трамваєм №{tram}, {stop_text}: " + " - ".join(stops))
        else:
            route_text.append(f"\nПересядьте на трамвай №{tram}, {stop_text}: " + " - ".join(stops))

    return ". ".join(route_text)


def get_all_stops_sorted(tram_routes):
    """
    Отримання усіх зупинок, на яких зупиняються трамваї,
    посортована за українським алфавітом

    tram_routes - словник з інформацією про трамвайні маршрути
    повертає: список усіх зупинок, на яких зупиняються трамваї, посортованих за українським алфавітом
    """
    ukraine_alphabet = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
    alphabet_index = {char: index for index, char in enumerate(ukraine_alphabet)}
    all_stops = set()
    for tram, routes in tram_routes.items():
        all_stops.update(routes[3])

    # Sort the stops using the custom key
    return sorted(all_stops, key=lambda x: [alphabet_index[char] for char in x.lower() if char in alphabet_index])


all_stops = get_all_stops_sorted(trams)


def how_many_stops(tram_routes, start_stop, end_stop):
    """
        Підрахунок кількості зупинок між двома зупинками

        tram_routes - словник з інформацією про трамвайні маршрути
        start_stop - назва початкової зупинки
        end_stop - назва кінцевої зупинки
        повертає: текст з інформацією про кількість зупинок та пересадок
        """
    route = find_best_route(tram_routes, start_stop, end_stop)
    if not route:
        return "Маршрут не знайдено. Перевірте коректність введених назв зупинок."

    total_stops = sum(count for _, _, count in route)
    transfers = len(route) - 1

    if total_stops == 1:
        stops_text = "1 зупинка"
    elif total_stops in [2, 3, 4]:
        stops_text = f"{total_stops} зупинки"
    else:
        stops_text = f"{total_stops} зупинок"

    if transfers == 1:
        transfers_text = "з 1 пересадкою"
    else:
        transfers_text = f"з {transfers} пересадками"

    if transfers == 0:
        return f"{stops_text} без пересадки."
    else:
        return f"{stops_text} {transfers_text}."


def open_route_window():
    """
    Відкриття вікна для пошуку маршруту між двома зупинками
    """
    route_window = tk.Toplevel()
    route_window.title("Пошук маршруту")

    label1 = tk.Label(route_window, text="Ви хочете дізнатись як потрапити з однієї зупинки на іншу?")
    label1.pack(pady=10)

    label2 = tk.Label(route_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    frame = tk.Frame(route_window)
    frame.pack(pady=10)

    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    search_button = tk.Button(frame, text="Пошуку маршруту",
                              command=lambda: find_route(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    result_text = tk.Text(route_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)


def find_route(start, end, result_text):
    """
        Пошук маршруту між двома зупинками та відображення результату

        start - назва початкової зупинки
        end - назва кінцевої зупинки
        result_text - текстове поле для відображення результату
        """
    result_text.delete(1.0, tk.END)

    if not start or not end:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, введіть усі необхідні дані.")
        return

    if start not in all_stops or end not in all_stops:
        result_text.insert(tk.END, "Маршрут не знайдено. Перевірте коректність введених назв зупинок.")
        return

    route_text = create_route_text(trams, start, end)
    result_text.insert(tk.END, route_text)


def open_how_many_stops_window():
    """
        Відкриття вікна для підрахунку кількості зупинок між двома зупинками
    """
    stops_window = tk.Toplevel()
    stops_window.title("Скільки зупинок")

    label1 = tk.Label(stops_window, text="Ви хочете дізнатись скільки зупинок між двома зупинками?")
    label1.pack(pady=10)

    label2 = tk.Label(stops_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    frame = tk.Frame(stops_window)
    frame.pack(pady=10, padx=25)

    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    search_button = tk.Button(frame, text="Пошукі зупинок",
                              command=lambda: find_stops(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    result_text = tk.Text(stops_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)


def find_stops(start, end, result_text):
    """
    Підрахунок кількості зупинок між двома зупинками та відображення результату

    start - назва початкової зупинки
    end - назва кінцевої зупинки
    result_text - текстове поле для відображення результату
    """
    result_text.delete(1.0, tk.END)

    # Check if fields are empty
    if not start or not end:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, введіть усі необхідні дані.")
        return

    # Check if entered stops are valid
    if start not in all_stops or end not in all_stops:
        result_text.insert(tk.END, "Маршрут не знайдено. Перевірте коректність введених назв зупинок.")
        return

    stops_text = how_many_stops(trams, start, end)
    result_text.insert(tk.END, stops_text)


def open_can_reach_window():
    """
    Відкриття вікна для перевірки можливості дістатися від однієї зупинки до іншої
    """
    reach_window = tk.Toplevel()
    reach_window.title("Чи можна дістатися")

    label1 = tk.Label(reach_window, text="Ви хочете дізнатись чи можна дістатися від однієї зупинки до іншої?")
    label1.pack(pady=10)

    label2 = tk.Label(reach_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    frame = tk.Frame(reach_window)
    frame.pack(pady=10, padx=25)

    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    search_button = tk.Button(frame, text="Перевірити можливість",
                              command=lambda: find_can_reach(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    result_text = tk.Text(reach_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)


def find_can_reach(start, end, result_text):
    """
    Перевірка можливості дістатися від однієї зупинки до іншої та відображення результату
    start - назва початкової зупинки
    end - назва кінцевої зупинки
    result_text - текстове поле для відображення результату
    """
    result_text.delete(1.0, tk.END)

    if not start or not end:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, введіть усі необхідні дані.")
        return

    if start not in all_stops or end not in all_stops:
        result_text.insert(tk.END, "Маршрут не знайдено. Перевірте коректність введених назв зупинок.")
        return

    route = find_best_route(trams, start, end)
    if not route:
        result_text.insert(tk.END, "Маршрут не знайдено. Перевірте коректність введених назв зупинок.")
        return

    if len(route) == 1:
        result_text.insert(tk.END, f"Можна, використовуючи трамвай №{route[0][0]}")
    else:
        transfers_text = "Можна, з пересадкою"
        for i in range(len(route) - 1):
            transfers_text += f" з трамваю №{route[i][0]} на трамвай №{route[i + 1][0]}"
        result_text.insert(tk.END, transfers_text)


def open_tram_route_window():
    """
    Відкриття вікна для відображення детального маршруту трамваю
    """
    tram_route_window = tk.Toplevel()
    tram_route_window.title("Детальний маршрут трамваю")

    label1 = tk.Label(tram_route_window, text="Виберіть номер трамваю для перегляду маршруту")
    label1.pack(pady=10)

    frame = tk.Frame(tram_route_window)
    frame.pack(pady=10, padx=25)

    tram_numbers = sorted(trams.keys())
    tram_label = tk.Label(frame, text="Номер трамваю:")
    tram_label.grid(row=0, column=0, padx=5, pady=5)
    tram_number = ttk.Combobox(frame, values=tram_numbers)
    tram_number.grid(row=0, column=1, padx=5, pady=5)

    show_button = tk.Button(frame, text="Показати маршрут",
                            command=lambda: show_tram_route(tram_number.get(), result_text))
    show_button.grid(row=1, column=0, columnspan=2, pady=10)

    result_text = tk.Text(tram_route_window, height=15, width=60, wrap=tk.WORD)
    result_text.pack(pady=10)


def show_tram_route(tram_number, result_text):
    """
    Відображення детального маршруту трамваю
    tram_number - номер трамваю
    result_text - текстове поле для відображення результату
    """
    result_text.delete(1.0, tk.END)

    if not tram_number or not tram_number.isdigit() or int(tram_number) not in trams:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, виберіть номер трамваю зі списку.")
        return

    tram_number = int(tram_number)
    route_info = trams[tram_number]
    route_name = route_info[0]
    direct_route = route_info[1]
    reverse_route = route_info[2]

    result_text.insert(tk.END, f"Маршрут №{tram_number}\n")
    result_text.insert(tk.END, f"{route_name}\n")
    result_text.insert(tk.END, f"Прямий напрямок:\n{' - '.join(direct_route)}\n")
    result_text.insert(tk.END, f"Зворотній напрямок:\n{' - '.join(reverse_route)}\n")

    G = nx.Graph()
    stops = direct_route + reverse_route
    for i in range(len(stops) - 1):
        G.add_edge(stops[i], stops[i + 1], tram=tram_number)

    plt.clf()

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42, k=0.02)

    tram_color = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

    nx.draw_networkx_nodes(G, pos, node_size=100, node_color="skyblue", edgecolors='k', ax=ax)

    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color=tram_color, ax=ax)

    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="light", ax=ax)

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        if (u, v) in edge_labels:
            edge_labels[(u, v)] += f", {data['tram']}"
        else:
            edge_labels[(u, v)] = str(data['tram'])

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

    if hasattr(show_tram_route, 'canvas') and show_tram_route.canvas:
        show_tram_route.canvas.get_tk_widget().destroy()

    show_tram_route.canvas = FigureCanvasTkAgg(fig, master=result_text.master)
    show_tram_route.canvas.draw()
    show_tram_route.canvas.get_tk_widget().pack(pady=10)


def open_tram_scheme_window():
    """
    Відкриття вікна для відображення схеми руху трамваїв міста
    """
    scheme_window = tk.Toplevel()
    scheme_window.title("Схема руху трамваїв міста")

    G = nx.Graph()

    for tram, routes in trams.items():
        stops = routes[1] + routes[2]
        for i in range(len(stops) - 1):
            G.add_edge(stops[i], stops[i + 1], tram=tram)

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42, k=0.02)

    tram_colors = {}
    for tram in trams.keys():
        tram_colors[tram] = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

    nx.draw_networkx_nodes(G, pos, node_size=100, node_color="green", edgecolors='k', ax=ax)

    for u, v, data in G.edges(data=True):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=tram_colors[data['tram']], ax=ax)

    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="light", ax=ax)

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        if (u, v) in edge_labels:
            edge_labels[(u, v)] += f", {data['tram']}"
        else:
            edge_labels[(u, v)] = str(data['tram'])

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

    canvas = FigureCanvasTkAgg(fig, master=scheme_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def get_protocole_of_testing():
    with open('InternalProtocole.txt', 'w', encoding='utf-8') as file:
        # Test the process_tram_file function
        file.write("Test the process_tram_file function\n")
        trams = process_tram_file('TramsInfo.txt')
        file.write(f"Number of trams: {len(trams)}\n")
        for tram, routes in trams.items():
            # write tram number
            file.write(f"Tram number: {tram}\n")
            # write route name
            file.write(f"Route name: {routes[0]}\n")
            # write direct route
            file.write(f"Direct route: {routes[1]}\n")
            # write reverse route
            file.write(f"Reverse route: {routes[2]}\n")
        file.write("\n")
        file.write("Test the find_trams_by_stop function\n")
        trams_by_stop = find_trams_by_stop(trams, "Залізничний вокзал")
        file.write("Expected result: [1, 4, 6, 9]\n")
        file.write(f"Trams by stop: {trams_by_stop}\n")
        file.write("\n")
        file.write("Test the find_best_route function\n")
        best_route = find_best_route(trams, "Залізничний вокзал", "Площа Ринок")
        file.write("Expected result: [(1, ['Залізничний вокзал', 'Приміський вокзал', 'Кропивницького', 'Старосольських', 'Львівська політехніка', 'Головна пошта', 'Дорошенка', 'Площа Ринок'], 7)]\n")
        file.write(f"Best route: {str(best_route)}")
        file.write("\n")
        file.close()

get_protocole_of_testing()

def find_trams_by_stop(stop_name, tram_routes):
    """
    Знаходить всі трамваї, що проходять через задану зупинку.
    """
    trams_by_stop = []
    for tram, route_info in tram_routes.items():
        if stop_name in route_info[-1]:
            trams_by_stop.append(tram)
    return trams_by_stop


def open_tram_through_stops_window():
    """
    Відкриття вікна для перевірки, чи є трамвай, що проходить через всі вибрані зупинки
    """
    stops_window = tk.Toplevel()
    stops_window.title("Пошук трамваю через зупинки")

    label1 = tk.Label(stops_window, text="Виберіть зупинки, через які має проходити трамвай:")
    label1.pack(pady=10)

    frame = tk.Frame(stops_window)
    frame.pack(pady=10, padx=25)

    all_stops = get_all_stops_sorted(trams)  # Отримуємо список всіх зупинок

    # Створюємо Listbox для вибору декількох зупинок
    stops_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10, width=50)
    for stop in all_stops:
        stops_listbox.insert(tk.END, stop)
    stops_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

    search_button = tk.Button(frame, text="Знайти трамвай",
                              command=lambda: handle_tram_search(stops_listbox, result_text))
    search_button.grid(row=1, column=0, columnspan=2, pady=10)

    result_text = tk.Text(stops_window, height=5, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)


def handle_tram_search(stops_listbox, result_text):
    """
    Обробка результату пошуку трамваю через вибрані зупинки
    """
    result_text.delete(1.0, tk.END)

    selected_stops = [stops_listbox.get(i) for i in stops_listbox.curselection()]  # Отримуємо вибрані зупинки
    if not selected_stops:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, виберіть хоча б одну зупинку.")
        return

    tram = find_tram_through_stops(selected_stops, trams)
    if tram:
        result_text.insert(tk.END, f"Трамвай №{tram} проходить через всі вибрані зупинки.")
    else:
        result_text.insert(tk.END, "Немає трамвая, який проходить через всі ці зупинки.")


def find_tram_through_stops(selected_stops, tram_routes):
    """
    Перевіряє, чи є трамвай, що проходить через всі вибрані зупинки

    Параметри:
    - selected_stops: список вибраних зупинок
    - tram_routes: словник маршрутів трамваїв

    Повертає:
    - номер трамваю, якщо він проходить через всі зупинки
    - None, якщо такого трамваю немає
    """
    for tram, route_info in tram_routes.items():
        tram_stops = route_info[-1]  # Множина всіх зупинок на маршруті (direct + reverse)
        if all(stop in tram_stops for stop in selected_stops):
            return tram
    return None



def open_trams_by_stop_window():
    """
    Відкриття вікна для пошуку трамваїв за зупинкою
    """
    trams_window = tk.Toplevel()
    trams_window.title("Пошук трамваїв за зупинкою")

    label1 = tk.Label(trams_window, text="Оберіть зупинку з випадаючого списку, щоб побачити доступні трамваї:")
    label1.pack(pady=10)

    all_stops = get_all_stops_sorted(trams)

    # Create a dropdown (Combobox) for selecting a stop
    frame = tk.Frame(trams_window)
    frame.pack(pady=10, padx=25)

    stop_label = tk.Label(frame, text="Зупинка:")
    stop_label.grid(row=0, column=0, padx=5, pady=5)
    stop_combobox = ttk.Combobox(frame, values=all_stops)
    stop_combobox.grid(row=0, column=1, padx=5, pady=5)

    # Text box for displaying trams that go through the selected stop
    result_text = tk.Text(trams_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)

    def show_trams():
        stop_name = stop_combobox.get()
        result_text.delete(1.0, tk.END)

        if stop_name not in all_stops:
            messagebox.showwarning("Невірна зупинка", "Оберіть зупинку зі списку.")
            return

        trams_at_stop = find_trams_by_stop(stop_name, trams)
        if trams_at_stop:
            result_text.insert(tk.END, f"Трамваї, що їдуть через {stop_name}: {', '.join(map(str, trams_at_stop))}")
        else:
            result_text.insert(tk.END, f"Трамваїв через {stop_name} не знайдено.")

    search_button = tk.Button(frame, text="Показати трамваї", command=show_trams)
    search_button.grid(row=1, column=0, columnspan=2, pady=10)




def main():
    """
    Головна функція для запуску головного вікна програми
    """
    root = tk.Tk()
    root.title("Довідник")

    # Center the window on the screen
    window_width = 1000
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    # Create a custom font for the bold text
    bold_font = font.Font(root, size=40, weight='bold')

    # Create and place the labels
    label1 = tk.Label(root, text="Довідка про Львівський трамвай", font=bold_font, fg='green')
    label1.pack(pady=10)

    label2 = tk.Label(root,
                      text="За допомогою цього застосунку ви можете проконсультувати схему руху трамваїв міста Лева.")
    label3 = tk.Label(root, text="Оберіть опцію серед запропонованих нижче:")
    label2.pack(pady=10, padx=10)
    label3.pack(pady=2)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Create and place the buttons
    button1 = tk.Button(button_frame, text="Як дістатися від однієї зупинки на іншу", width=30, height=2,
                        command=open_route_window)
    button1.grid(row=0, column=0, padx=5, pady=5)

    button2 = tk.Button(button_frame, text="Чи можна дістатися від зупинки на іншу", width=30, height=2,
                        command=open_can_reach_window)
    button2.grid(row=0, column=1, padx=5, pady=5)

    button3 = tk.Button(button_frame, text="Cкільки зупинок від зупинки до іншої", width=30, height=2,
                        command=open_how_many_stops_window)
    button3.grid(row=0, column=2, padx=5, pady=5)

    button4 = tk.Button(button_frame, text="Детальний маршрут трамваю", width=30, height=2,
                        command=open_tram_route_window)
    button4.grid(row=1, column=0, padx=5, pady=5)

    button5 = tk.Button(button_frame, text="Схема руху трамваїв міста", width=30, height=2,
                        command=open_tram_scheme_window)
    button5.grid(row=1, column=1, padx=5, pady=5)

    button6 = tk.Button(button_frame, text="Пошук трамваїв за зупинкою", width=30, height=2,
                        command=open_trams_by_stop_window)
    button6.grid(row=1, column=2, padx=5, pady=5)

    button7 = tk.Button(button_frame, text="Перевірити трамвай за зупинками", width=30, height=2,
                        command=open_tram_through_stops_window)  
    button7.grid(row=2, column=0, columnspan=3, pady=10)  

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
