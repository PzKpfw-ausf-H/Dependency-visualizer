import unittest
from unittest.mock import patch, mock_open, MagicMock
import requests
import json
from io import StringIO

from dependency_visualizer import read_config, fetch_package_json, get_dependencies, generate_graphviz_code


class TestDependencyVisualizer(unittest.TestCase):
    def test_read_config(self):
        # Подготовка данных
        mock_csv = "graphviz_path,package_name,output_path\nC:\\Graphviz\\bin,react,output.dot\n"

        # Используем mock_open для имитации файла
        with patch("builtins.open", mock_open(read_data=mock_csv)):
            graphviz_path, package_name, output_path = read_config("mock_config.csv")

        # Проверяем результат
        self.assertEqual(graphviz_path, "C:\\Graphviz\\bin")
        self.assertEqual(package_name, "react")
        self.assertEqual(output_path, "output.dot")

    @patch("requests.get")
    def test_fetch_package_json(self, mock_get):
        # Подготовка данных
        package_name = "react"
        mock_response = {
            "name": "react",
            "dependencies": {"loose-envify": "^1.1.0"}
        }

        # Настраиваем mock для requests.get
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)

        # Вызываем функцию
        result = fetch_package_json(package_name)

        # Проверяем результат
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with(f"https://registry.npmjs.org/{package_name}/latest")

    @patch("requests.get")
    def test_get_dependencies(self, mock_get):
        # Подготовка данных
        package_name = "react"
        mock_responses = {
            "react": {"dependencies": {"loose-envify": "^1.1.0"}},
            "loose-envify": {"dependencies": {"js-tokens": "^3.0.0"}},
            "js-tokens": {"dependencies": {}}
        }

        # Настраиваем mock для requests.get
        def mock_get_side_effect(url):
            package = url.split("/")[-2]
            response = mock_responses.get(package, {})
            return MagicMock(status_code=200, json=lambda: response)

        mock_get.side_effect = mock_get_side_effect

        # Вызываем функцию
        result = get_dependencies(package_name)

        # Ожидаемый результат
        expected = {
            "react": ["loose-envify"],
            "loose-envify": ["js-tokens"],
            "js-tokens": []
        }

        # Проверяем результат
        self.assertEqual(result, expected)

    def test_generate_graphviz_code(self):
        # Входные данные
        dependencies = {
            "react": ["loose-envify"],
            "loose-envify": ["js-tokens"],
            "js-tokens": []
        }

        # Вызываем функцию
        result = generate_graphviz_code(dependencies)

        # Ожидаемый результат
        expected = (
            "digraph dependencies {\n"
            '    "react" -> "loose-envify";\n'
            '    "loose-envify" -> "js-tokens";\n'
            "}"
        )

        # Проверяем результат
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.dependency_visualizer()