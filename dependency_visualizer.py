import csv
import json
import requests
import sys


# Функция для чтения конфигурационного файла CSV
def read_config(config_file):
    with open(config_file, mode='r') as file:
        reader = csv.DictReader(file)
        config = next(reader)
    return config['graphviz_path'], config['package_name'], config['output_path']


# Функция для загрузки package.json пакета с npm
def fetch_package_json(package_name):
    url = f"https://registry.npmjs.org/{package_name}/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Не удалось получить package.json для {package_name}")
        return None


# Рекурсивная функция для сбора зависимостей
def get_dependencies(package_name, dependencies=None, visited=None):
    if dependencies is None:
        dependencies = {}
    if visited is None:
        visited = set()

    # Пропускаем уже посещенные пакеты
    if package_name in visited:
        return dependencies

    visited.add(package_name)

    # Получаем package.json с npm
    package_data = fetch_package_json(package_name)
    if not package_data:
        return dependencies

    # Извлекаем зависимости из package.json
    package_dependencies = package_data.get("dependencies", {})
    dependencies[package_name] = list(package_dependencies.keys())

    # Рекурсивный сбор зависимостей
    for dep in package_dependencies:
        get_dependencies(dep, dependencies, visited)

    return dependencies


# Функция для создания Graphviz представления зависимостей
def generate_graphviz_code(dependencies):
    graph = ["digraph dependencies {"]
    for package, deps in dependencies.items():
        for dep in deps:
            graph.append(f'    "{package}" -> "{dep}";')
    graph.append("}")
    return "\n".join(graph)


# Основная функция для работы с конфигурацией, сборки зависимостей и генерации Graphviz кода
def main(config_file):
    graphviz_path, package_name, output_path = read_config(config_file)
    dependencies = get_dependencies(package_name)
    graphviz_code = generate_graphviz_code(dependencies)

    with open(output_path, "w") as f:
        f.write(graphviz_code)

    print(graphviz_code)


if __name__ == "__main__":
    config_file = sys.argv[1]
    main(config_file)
