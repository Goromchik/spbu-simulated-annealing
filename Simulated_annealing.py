import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import math
import time
import random
import numpy as np


class GraphBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Метод имитации отжига")
        self.root.geometry("1200x800")
        self.graph = nx.Graph()
        self.nodes = {}
        self.edges = []
        self.node_counter = 0
        self.selected_node = None
        self.standard_results = ""
        self.modified_results = ""

        self.edges_frame = tk.LabelFrame(self.root, text="Ребра", padx=5, pady=5)
        self.edges_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        columns = ("Вершина 1", "Вершина 2", "Длина")
        self.edges_table = ttk.Treeview(self.edges_frame, columns=columns, show="headings")
        for col in columns:
            self.edges_table.heading(col, text=col)
        self.edges_table.grid(row=0, column=0, sticky="ew")

        self.parameters_frame = tk.LabelFrame(self.root, text="Параметры алгоритма", padx=5, pady=5)
        self.parameters_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(self.parameters_frame, text="Начальная температура:").grid(row=0, column=0, sticky="w")
        self.initial_temp_entry = tk.Entry(self.parameters_frame)
        self.initial_temp_entry.insert(0, "1000")
        self.initial_temp_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(self.parameters_frame, text="Скорость охлаждения:").grid(row=1, column=0, sticky="w")
        self.cooling_rate_entry = tk.Entry(self.parameters_frame)
        self.cooling_rate_entry.insert(0, "0.003")
        self.cooling_rate_entry.grid(row=1, column=1, sticky="ew")

        tk.Label(self.parameters_frame, text="Количество итераций:").grid(row=2, column=0, sticky="w")
        self.iterations_entry = tk.Entry(self.parameters_frame)
        self.iterations_entry.insert(0, "1000")
        self.iterations_entry.grid(row=2, column=1, sticky="ew")

        # Кнопки
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.calculate_button = tk.Button(self.buttons_frame, text="Рассчитать", command=self.calculate_path)
        self.calculate_button.grid(row=0, column=0, padx=5)

        self.calculate_mod_button = tk.Button(self.buttons_frame, text="Рассчитать с модификацией",
                                            command=self.calculate_path_with_modification)
        self.calculate_mod_button.grid(row=0, column=1, padx=5)

        self.clear_button = tk.Button(self.buttons_frame, text="Очистить", command=self.clear_all)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.create_connected_graph_button = tk.Button(self.buttons_frame, text="Создать связный граф",
                                                     command=self.create_connected_graph)
        self.create_connected_graph_button.grid(row=0, column=3, padx=5)

        self.result_frame = tk.LabelFrame(self.root, text="Результаты", padx=5, pady=5)
        self.result_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew", rowspan=4)

        self.result_text = tk.Text(self.result_frame, height=15, width=50, wrap=tk.WORD, font=('Arial', 10))
        self.result_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.config(yscrollcommand=scrollbar.set)

        self.canvas_frame = tk.LabelFrame(self.root, text="Граф", padx=5, pady=5)
        self.canvas_frame.grid(row=0, column=1, rowspan=8, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.original_graph_frame = tk.LabelFrame(self.root, text="Исходный граф с кратчайшим путем", padx=5, pady=5)
        self.original_graph_frame.grid(row=0, column=2, rowspan=8, padx=10, pady=10, sticky="nsew")

        self.original_graph_canvas = tk.Canvas(self.original_graph_frame, bg="white")
        self.original_graph_canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

    # Метод для создания связного графа
    def create_connected_graph(self):
        num_nodes = simpledialog.askinteger("Создать связный граф", "Введите количество вершин:")
        if num_nodes is None or num_nodes < 3:
            messagebox.showwarning("Ошибка", "Количество вершин должно быть не менее 3")
            return

        self.clear_all()

        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(num_nodes))
        self.node_counter = num_nodes

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        min_distance = 50

        for node in self.graph.nodes:
            while True:
                x = random.randint(50, canvas_width - 50)
                y = random.randint(50, canvas_height - 50)
                overlap = False

                for existing_node, (ex, ey) in self.nodes.items():
                    if math.sqrt((x - ex) ** 2 + (y - ey) ** 2) < min_distance:
                        overlap = True
                        break

                if not overlap:
                    self.nodes[node] = (x, y)
                    break

        hamiltonian_cycle = list(range(num_nodes))
        for i in range(num_nodes):
            node1 = i
            node2 = (i + 1) % num_nodes
            length = random.randint(10, 100)
            self.graph.add_edge(node1, node2, weight=length)
            self.edges.append((node1, node2, length))

        extra_edges = 2 * num_nodes
        for _ in range(extra_edges):
            while True:
                node1 = random.randint(0, num_nodes - 1)
                node2 = random.randint(0, num_nodes - 1)
                if node1 != node2 and not self.graph.has_edge(node1, node2):
                    length = random.randint(10, 100)
                    self.graph.add_edge(node1, node2, weight=length)
                    self.edges.append((node1, node2, length))
                    break

        if not nx.is_connected(self.graph):
            messagebox.showwarning("Ошибка", "Граф не связный после создания")
            return

        print("Вершины:", self.graph.nodes)
        print("Рёбра:", self.graph.edges)
        print("Граф связный:", nx.is_connected(self.graph))
        print("Гамильтонов цикл:", hamiltonian_cycle)

        self.update_edges_table()
        self.draw_graph()

    # Обработка клика на холсте: добавление узла или ребра
    def on_canvas_click(self, event):
        clicked_node = self.find_node(event.x, event.y)
        if clicked_node is not None:
            if self.selected_node is None:
                self.selected_node = clicked_node
            else:
                if self.selected_node != clicked_node:
                    self.add_edge(self.selected_node, clicked_node)
                    self.selected_node = None
        else:
            node_id = self.node_counter
            self.nodes[node_id] = (event.x, event.y)
            self.graph.add_node(node_id)
            self.node_counter += 1
            self.draw_graph()

    # Обработка правого клика на холсте: удаление или изменение ребра
    def on_canvas_right_click(self, event):
        clicked_edge = self.find_edge(event.x, event.y)
        if clicked_edge:
            self.show_edge_context_menu(event, clicked_edge)
        else:
            self.selected_node = None

    # Отображение меню для ребра
    def show_edge_context_menu(self, event, edge):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Изменить длину", command=lambda: self.edit_edge_length(edge))
        context_menu.add_command(label="Удалить ребро", command=lambda: self.remove_edge(edge))
        context_menu.post(event.x_root, event.y_root)

    # Изменение длины ребра
    def edit_edge_length(self, edge):
        new_length = simpledialog.askfloat("Изменить длину ребра",
                                           f"Введите новую длину ребра между вершинами {edge[0]} и {edge[1]}:")
        if new_length is None or new_length <= 0:
            messagebox.showwarning("Ошибка", "Длина ребра должна быть положительным числом")
            return

        self.graph[edge[0]][edge[1]]['weight'] = new_length
        for i, e in enumerate(self.edges):
            if e[0] == edge[0] and e[1] == edge[1]:
                self.edges[i] = (e[0], e[1], new_length)
                break

        self.update_edges_table()
        self.draw_graph()

    # Поиск узла по координатам
    def find_node(self, x, y):
        for node, (nx, ny) in self.nodes.items():
            if (nx - x) ** 2 + (ny - y) ** 2 <= 400:
                return node
        return None

    # Поиск ребра по координатам
    def find_edge(self, x, y):
        for edge in self.edges:
            node1, node2, _ = edge
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]

            dx = x2 - x1
            dy = y2 - y1
            length_squared = dx ** 2 + dy ** 2
            if length_squared == 0:
                continue

            t = ((x - x1) * dx + (y - y1) * dy) / length_squared
            t = max(0, min(1, t))

            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

            distance_squared = (x - closest_x) ** 2 + (y - closest_y) ** 2

            if distance_squared <= 25:
                return edge
        return None

    # Добавление ребра между двумя узлами
    def add_edge(self, node1, node2):
        edge = tuple(sorted((node1, node2)))
        if edge in [tuple(sorted((e[0], e[1]))) for e in self.edges]:
            messagebox.showwarning("Ошибка", f"Ребро между вершинами {node1} и {node2} уже существует.")
            return
        if node1 not in self.nodes or node2 not in self.nodes:
            messagebox.showwarning("Ошибка", f"Вершины {node1} или {node2} не существуют в графе.")
            return
        length = simpledialog.askfloat("Длина ребра", f"Введите длину ребра между вершинами {node1} и {node2}:")
        if length is None or length <= 0:
            messagebox.showwarning("Ошибка", "Длина ребра должна быть положительным числом")
            return
        self.graph.add_edge(node1, node2, weight=length)
        self.edges.append((node1, node2, length))
        self.update_edges_table()
        self.draw_graph()

    # Удаление ребра
    def remove_edge(self, edge):
        node1, node2, _ = edge
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)
            self.edges.remove(edge)
            self.update_edges_table()
            self.draw_graph()

    # Расчет пути методом имитации отжига
    def calculate_path(self):
        if len(self.nodes) < 3:
            messagebox.showwarning("Ошибка", "Добавьте минимум 3 вершины")
            return

        try:
            initial_temp = float(self.initial_temp_entry.get())
            cooling_rate = float(self.cooling_rate_entry.get())
            iterations = int(self.iterations_entry.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректные параметры алгоритма")
            return

        start_time = time.time()
        path, distance = self.simulated_annealing(initial_temp, cooling_rate, iterations)
        elapsed_time = time.time() - start_time

        if isinstance(distance, str):
            messagebox.showwarning("Ошибка", distance)
            return

        # Обновляем только стандартные результаты
        self.standard_results = f"Стандартный метод\n"
        self.standard_results += f"Путь: {' → '.join(map(str, path))}\n"
        self.standard_results += f"Длина: {distance:.2f}\n"
        self.standard_results += f"Время: {elapsed_time:.4f} сек\n\n"

        self.update_result_text()
        self.draw_path(path)

    # Проверка на существование гамильтонова цикла
    def has_hamiltonian_cycle(self):
        try:
            cycle = nx.find_cycle(self.graph, source=0)
            return True
        except nx.NetworkXNoCycle:
            return False

    # Расчет пути с модификацией (многократный запуск)
    def calculate_path_with_modification(self):
        if len(self.nodes) < 3:
            messagebox.showwarning("Ошибка", "Добавьте минимум 3 вершины")
            return

        try:
            initial_temp = float(self.initial_temp_entry.get())
            cooling_rate = float(self.cooling_rate_entry.get())
            iterations = int(self.iterations_entry.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректные параметры алгоритма")
            return

        start_time = time.time()
        path, distance = self.simulated_annealing_cauchy(initial_temp, cooling_rate, iterations)
        elapsed_time = time.time() - start_time

        if isinstance(distance, str):
            messagebox.showwarning("Ошибка", distance)
            return

        self.modified_results = f"Модифицированный метод\n"
        self.modified_results += f"Путь: {' → '.join(map(str, path))}\n"
        self.modified_results += f"Длина: {distance:.2f}\n"
        self.modified_results += f"Время: {elapsed_time:.4f} сек\n"

        self.update_result_text()
        self.draw_path(path)

    # Обновление текстового поля с результатами
    def update_result_text(self):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, self.standard_results)
        self.result_text.insert(tk.END, self.modified_results)

    # Реализация алгоритма имитации отжига
    def simulated_annealing(self, initial_temp, cooling_rate, num_iterations):
        current_solution = list(self.graph.nodes)
        random.shuffle(current_solution)
        current_solution.append(current_solution[0])
        current_distance = self.calculate_path_distance(current_solution)

        if current_distance is None:
            return None, "Невозможно построить маршрут (граф не связный)"

        best_solution = current_solution.copy()
        best_distance = current_distance

        temp = initial_temp

        for _ in range(num_iterations):
            neighbor = current_solution[:-1].copy()
            a, b = random.sample(range(len(neighbor)), 2)
            neighbor[a], neighbor[b] = neighbor[b], neighbor[a]
            neighbor.append(neighbor[0])

            neighbor_distance = self.calculate_path_distance(neighbor)

            if neighbor_distance is None:
                continue

            if temp < 1e-10:
                break

            delta = neighbor_distance - current_distance

            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_solution = neighbor
                current_distance = neighbor_distance

                if current_distance < best_distance:
                    best_solution = current_solution.copy()
                    best_distance = current_distance

            temp *= 1 - cooling_rate

        return best_solution, best_distance

    # Модификация Коши
    def simulated_annealing_cauchy(self, initial_temp, cooling_rate, num_iterations):
        current_solution = list(self.graph.nodes)
        random.shuffle(current_solution)
        current_solution.append(current_solution[0])
        current_distance = self.calculate_path_distance(current_solution)

        temp = initial_temp
        best_solution = current_solution.copy()
        best_distance = current_distance

        for _ in range(num_iterations):
            neighbor = current_solution[:-1].copy()
            a, b = random.sample(range(len(neighbor)), 2)
            neighbor[a], neighbor[b] = neighbor[b], neighbor[a]
            neighbor.append(neighbor[0])
            neighbor_distance = self.calculate_path_distance(neighbor)

            delta = neighbor_distance - current_distance

            try:
                if delta < 0 or (temp > 1e-10 and random.random() < 1 / (1 + (delta / temp) ** 2)):
                    current_solution = neighbor
                    current_distance = neighbor_distance
                    if current_distance < best_distance:
                        best_solution = current_solution.copy()
                        best_distance = current_distance
            except OverflowError:
                pass

            temp *= 1 - cooling_rate

        return best_solution, best_distance

    # Расчет длины пути
    def calculate_path_distance(self, path):
        total_distance = 0
        missing_edges = []

        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i + 1]):
                total_distance += self.graph[path[i]][path[i + 1]]['weight']
            else:
                try:
                    shortest_path = nx.shortest_path_length(self.graph, path[i], path[i + 1], weight='weight')
                    total_distance += shortest_path
                    missing_edges.append((path[i], path[i + 1]))
                except nx.NetworkXNoPath:
                    return None

        if missing_edges:
            print(f"Использованы обходные пути для ребер: {missing_edges}")
        return total_distance

    # Обновление таблицы ребер
    def update_edges_table(self):
        self.edges_table.delete(*self.edges_table.get_children())
        for edge in self.edges:
            node1, node2, length = edge
            self.edges_table.insert("", "end", values=(node1, node2, length))

    # Отрисовка графа на холсте
    def draw_graph(self):
        self.canvas.delete("all")
        for node, (x, y) in self.nodes.items():
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="lightblue", outline="blue", width=3)
            self.canvas.create_text(x, y, text=str(node), font=("Arial", 14, "bold"), fill="darkblue")

        for edge in self.edges:
            node1, node2, _ = edge
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist == 0:
                continue

            start_x = x1 + (dx / dist) * 20
            start_y = y1 + (dy / dist) * 20
            end_x = x2 - (dx / dist) * 20
            end_y = y2 - (dy / dist) * 20

            self.canvas.create_line(start_x, start_y, end_x, end_y, fill="black", width=3, arrow=tk.BOTH)

    # Отрисовка пути на холсте
    def draw_path(self, path):
        self.original_graph_canvas.delete("all")
        for node, (x, y) in self.nodes.items():
            self.original_graph_canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="lightblue", outline="blue",
                                                   width=3)
            self.original_graph_canvas.create_text(x, y, text=str(node), font=("Arial", 14, "bold"), fill="darkblue")

        # Отрисовка всех рёбер графа
        for edge in self.edges:
            node1, node2, _ = edge
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist == 0:
                continue

            start_x = x1 + (dx / dist) * 20
            start_y = y1 + (dy / dist) * 20
            end_x = x2 - (dx / dist) * 20
            end_y = y2 - (dy / dist) * 20

            self.original_graph_canvas.create_line(start_x, start_y, end_x, end_y, fill="gray", width=1)

        # Отрисовка пути
        for i in range(len(path) - 1):
            node1, node2 = path[i], path[i + 1]
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist == 0:
                continue

            start_x = x1 + (dx / dist) * 20
            start_y = y1 + (dy / dist) * 20
            end_x = x2 - (dx / dist) * 20
            end_y = y2 - (dy / dist) * 20

            self.original_graph_canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=3, arrow=tk.LAST)

            if not self.graph.has_edge(node1, node2):
                self.original_graph_canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=3, dash=(4, 2))

    # Очистка всех данных и интерфейса
    def clear_all(self):
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        self.node_counter = 0
        self.selected_node = None
        self.standard_results = ""
        self.modified_results = ""
        self.edges_table.delete(*self.edges_table.get_children())
        self.result_text.delete(1.0, tk.END) 
        self.canvas.delete("all")
        self.original_graph_canvas.delete("all")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphBuilder(root)
    root.mainloop()