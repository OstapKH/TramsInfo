def process_tram_file(file_path):
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


# Example usage
file_path = 'TramsInfo.txt'  # Path to your file
trams = process_tram_file(file_path)

# Output the structured data
for tram_id, tram_info in trams.items():
    print(f"Трамвай {tram_id}: {tram_info}")