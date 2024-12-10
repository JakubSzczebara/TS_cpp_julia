import subprocess
import re
import random
import csv
import os 



# Funkcja do generowania początkowej ścieżki na podstawie wielkości instancji
def generate_initial_path(instance_name):
    # Wyodrębniamy liczbę z nazwy instancji
    match = re.search(r'(\d+)', instance_name)
    if not match:
        raise ValueError(f"Nie udało się znaleźć wielkości instancji w nazwie {instance_name}")
    size = int(match.group(1))
    
    # Generujemy początkową ścieżkę jako sekwencję liczb od 0 do size-1 (lub w inny sposób)
    initial_path = list(range(size))
    random.shuffle(initial_path)  # Można dodatkowo losowo ją przetasować
    
    output_filename = f"startPath.txt"
    with open(output_filename, "w") as file:
        file.write(" ".join(map(str, initial_path)))

# Funkcja do uruchamiania programu i zbierania wyników
def run_program(command, instance_name):
    # Uruchamiamy program
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    # Szukamy w wyniku linii z informacjami o kosztach, czasie i ścieżce
    match = re.search(r"cost:\s*([0-9]*\.?[0-9]+),\s*time:\s*(\d+),\s*path:\s*\[([0-9,\s]+)\]", result.stdout)

    if match:
        # Parsujemy wyniki
        cost = float(match.group(1))
        time = int(match.group(2))
        return {"cost": cost, "time": time}
    else:
        print(f"Nie znaleziono wyników dla instancji: {instance_name}")
        return None

# Funkcja do wczytywania instancji z pliku
def load_instances(filename):
    with open(filename, 'r') as file:
        instances = file.readlines()
    return [instance.strip() for instance in instances]

# Funkcja do uruchamiania testów
def run_tests(instances_file, program_cpp, program_julia, num_tests):
    results = {
            "cpp_results": {},
            "julia_results": {}
        }
    
    # Wczytujemy instancje
    instances = load_instances(instances_file)
    
    for instance in instances:
        results["cpp_results"][instance] = []
        results["julia_results"][instance] = []
        # Uruchamiamy testy 10 razy dla każdej instancji
        for i in range(num_tests):
            results["cpp_results"][instance].append([])
            results["julia_results"][instance].append([])
            
            generate_initial_path(instance)

            print(f"Uruchamiam test dla instancji {instance} (C++)...")
            cpp_command = ["taskset", "-c", "0", program_cpp, instance]  # Zakładamy, że programCpp przyjmuje nazwę instancji jako argument
            cpp_result = run_program(cpp_command, instance)
            if cpp_result:
                results["cpp_results"][instance][i].append(cpp_result['cost'])
                results["cpp_results"][instance][i].append(cpp_result['time'])
            
            
            print(f"Uruchamiam test dla instancji {instance} (Julia)...")
            julia_command = ["taskset", "-c", "0", "julia", program_julia, instance] # Zakładamy, że tsJulia.jl również przyjmuje nazwę instancji
            julia_result = run_program(julia_command, instance)
            if julia_result:
                results["julia_results"][instance][i].append(julia_result['cost'])
                results["julia_results"][instance][i].append(julia_result['time'])

    return results

# Główna część programu
if __name__ == "__main__":
    instances_file = "instances.txt" 
    program_cpp = "./tsCpp"  
    program_julia = "tsJulia.jl"  

    # Uruchamiamy testy
    results = run_tests(instances_file, program_cpp, program_julia, 20)
    print("\n\nKoniec")


    with open("results.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Zapisujemy nagłówki
        writer.writerow(["Instance", "Test", "Language", "Time"])
        
        # Zapisujemy wyniki C++
        for instance, cpp_tests in results["cpp_results"].items():
            for test_index, cpp_result in enumerate(cpp_tests):
                if cpp_result:  # Sprawdzamy, czy wynik istnieje
                    writer.writerow([os.path.splitext(instance)[0], test_index + 1, "C++", cpp_result[1]])
        
        # Zapisujemy wyniki Julia
        for instance, julia_tests in results["julia_results"].items():
            for test_index, julia_result in enumerate(julia_tests):
                if julia_result:  # Sprawdzamy, czy wynik istnieje
                    writer.writerow([os.path.splitext(instance)[0], test_index + 1, "Julia", julia_result[1]])
    
    

