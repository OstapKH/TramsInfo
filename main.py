from collections import deque

import tkinter as tk
from tkinter import font, ttk, messagebox


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
                            return path + [(tram, routes[direction][start_index:routes[direction].index(next_stop) + 1], routes[direction].index(next_stop) - start_index)]
                        if (next_stop, transfers + 1) not in visited:
                            queue.append((next_stop, path + [(tram, routes[direction][start_index:routes[direction].index(next_stop) + 1], routes[direction].index(next_stop) - start_index)], transfers + 1))

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
    # Create a new window
    route_window = tk.Toplevel()
    route_window.title("Пошук маршруту")

    # Create and place the labels
    label1 = tk.Label(route_window, text="Ви хочете дізнатись як потрапити з однієї зупинки на іншу?")
    label1.pack(pady=10)

    label2 = tk.Label(route_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    # Create a frame to hold the dropdowns and button
    frame = tk.Frame(route_window)
    frame.pack(pady=10)

    # Create and place the dropdowns
    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    # Create and place the search button
    search_button = tk.Button(frame, text="Пошуку маршруту", command=lambda: find_route(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Create and place the result text field
    result_text = tk.Text(route_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)


def find_route(start, end, result_text):
    result_text.delete(1.0, tk.END)

    # Check if fields are empty
    if not start or not end:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, введіть усі необхідні дані.")
        return

    # Check if entered stops are valid
    if start not in all_stops or end not in all_stops:
        result_text.insert(tk.END, "Маршрут не знайдено. Перевірте коректність введених назв зупинок.")
        return

    route_text = create_route_text(trams, start, end)
    result_text.insert(tk.END, route_text)

def open_how_many_stops_window():
    # Create a new window
    stops_window = tk.Toplevel()
    stops_window.title("Скільки зупинок")

    # Create and place the labels
    label1 = tk.Label(stops_window, text="Ви хочете дізнатись скільки зупинок між двома зупинками?")
    label1.pack(pady=10)

    label2 = tk.Label(stops_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    # Create a frame to hold the dropdowns and button
    frame = tk.Frame(stops_window)
    frame.pack(pady=10)

    # Create and place the dropdowns
    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    # Create and place the search button
    search_button = tk.Button(frame, text="Пошуку зупинок", command=lambda: find_stops(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Create and place the result text field
    result_text = tk.Text(stops_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)

def find_stops(start, end, result_text):
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
    # Create a new window
    reach_window = tk.Toplevel()
    reach_window.title("Чи можна дістатися")

    # Create and place the labels
    label1 = tk.Label(reach_window, text="Ви хочете дізнатись чи можна дістатися від однієї зупинки до іншої?")
    label1.pack(pady=10)

    label2 = tk.Label(reach_window, text="Виберіть з списку назви трамвайних зупинок")
    label2.pack(pady=10)

    # Create a frame to hold the dropdowns and button
    frame = tk.Frame(reach_window)
    frame.pack(pady=10)

    # Create and place the dropdowns
    all_stops = get_all_stops_sorted(trams)

    start_label = tk.Label(frame, text="Початкова зупинка:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_stop = ttk.Combobox(frame, values=all_stops)
    start_stop.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(frame, text="Зупинка-призначення:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_stop = ttk.Combobox(frame, values=all_stops)
    end_stop.grid(row=1, column=1, padx=5, pady=5)

    # Create and place the search button
    search_button = tk.Button(frame, text="Перевірити можливість", command=lambda: find_can_reach(start_stop.get(), end_stop.get(), result_text))
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Create and place the result text field
    result_text = tk.Text(reach_window, height=10, width=50, wrap=tk.WORD)
    result_text.pack(pady=10)

def find_can_reach(start, end, result_text):
    result_text.delete(1.0, tk.END)

    # Check if fields are empty
    if not start or not end:
        messagebox.showwarning("Недостатньо даних", "Будь ласка, введіть усі необхідні дані.")
        return

    # Check if entered stops are valid
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

def main():
    # Create the main window
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
    button1 = tk.Button(button_frame, text="Як дістатися від однієї зупинки на іншу", width=30, height=2, command=open_route_window)
    button1.grid(row=0, column=0, padx=5, pady=5)

    button2 = tk.Button(button_frame, text="Чи можна дістатися від зупинки на іншу", width=30, height=2,
                        command=open_can_reach_window)
    button2.grid(row=0, column=1, padx=5, pady=5)

    button3 = tk.Button(button_frame, text="Cкільки зупинок від зупинки до іншої", width=30, height=2, command=open_how_many_stops_window)
    button3.grid(row=0, column=2, padx=5, pady=5)

    button4 = tk.Button(button_frame, text="Детальний маршрут трамваю", width=30, height=2)
    button4.grid(row=1, column=0, padx=5, pady=5)

    button5 = tk.Button(button_frame, text="Схема руху трамваїв міста", width=30, height=2)
    button5.grid(row=1, column=1, padx=5, pady=5)

    button6 = tk.Button(button_frame, text="Текстовий режим отримання інформації", width=30, height=2)
    button6.grid(row=1, column=2, padx=5, pady=5)

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()