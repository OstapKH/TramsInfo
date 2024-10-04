from collections import deque

import tkinter as tk
from tkinter import font

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
                            return path + [(tram, routes[direction][start_index:routes[direction].index(next_stop) + 1], routes[direction].index(next_stop) - start_index)]
                        if (next_stop, transfers + 1) not in visited:
                            queue.append((next_stop, path + [(tram, routes[direction][start_index:routes[direction].index(next_stop) + 1], routes[direction].index(next_stop) - start_index)], transfers + 1))

    return None

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

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Довідник")

    # Create a custom font for the bold text
    bold_font = font.Font(root, size=12, weight='bold')

    # Create and place the labels
    label1 = tk.Label(root, text="Довідка про Львівський трамвай", font=bold_font, fg='green')
    label1.pack(pady=10)

    label2 = tk.Label(root, text="За допомогою цього застосунку ви можете проконсультувати схему руху трамваїв міста Лева.")
    label3 = tk.Label(root, text="Оберіть опцію серед запропонованих нижче:")
    label2.pack(pady=10, padx=10)
    label3.pack(pady=2)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Create and place the buttons
    button1 = tk.Button(button_frame, text="Як дістатися від однієї зупинки на іншу", width=30, height=2)
    button1.grid(row=0, column=0, padx=5, pady=5)

    button2 = tk.Button(button_frame, text="Чи можна дістатися від зупинки на іншу", width=30, height=2)
    button2.grid(row=0, column=1, padx=5, pady=5)

    button3 = tk.Button(button_frame, text="Cкільки зупинок від зупинки до іншої", width=30, height=2)
    button3.grid(row=0, column=2, padx=5, pady=5)

    button4 = tk.Button(button_frame, text="Детальний маршрут трамваю", width=30, height=2)
    button4.grid(row=1, column=0, padx=5, pady=5)

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()

