from collections import deque
import copy
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time  # <<-- Zaman ölçümü için eklendi
import heapq


def launch_solver(grid, algo, start_type):
    root = tk.Tk()
    app = SolverGUI(root, grid, algo, start_type)
    root.mainloop()

class SolverGUI:
    def __init__(self, root, grid_size, algorithm, start_type):
        self.root = root
        self.grid_size = grid_size
        self.algorithm = algorithm
        self.start_type = start_type
        
        self.root.title("Puzzle Solution Screen")
        self.root.state('zoomed')

        self.solution_steps = None
        self.current_step = 0
        self.found_solution = False
        self.rows, self.cols = self.get_grid_dimensions(grid_size)
        self.iteration_count = 0

        # Yeni eklenen değişkenler:
        self.start_time = None
        self.end_time = None
        self.nodes_expanded = 0
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Segoe UI', 13))

        self.puzzle_state = self.initialize_puzzle()


        if self.puzzle_state is None:
            messagebox.showerror("Hata", "Puzzle başlangıç durumu oluşturulamadı.")
            self.root.destroy()
            return


        self.cancelled = False  # Arama iptal edildi mi kontrolü


        title_text = f"Algorithm: {self.algorithm} | Grill: {self.grid_size} | Inception: {self.start_type}"
        self.title_label = ttk.Label(root, text=title_text, font=('Segoe UI', 16, 'bold'))
        self.title_label.pack(pady=10)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.grid_frame = tk.Frame(self.canvas)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.grid_frame,
            anchor="nw",
            width=self.canvas.winfo_width()
        )

        self.grid_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.info_label = ttk.Label(root, text=f"İterasyon: {self.iteration_count}", font=('Segoe UI', 13))
        self.info_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.step_button = ttk.Button(button_frame, text="Step", command=self.next_step)
        self.step_button.pack(side='left', padx=5)


        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_search)
        self.cancel_button.pack(side='left', padx=5)

        self.is_paused = False
        self.pause_resume_button = ttk.Button(button_frame, text="Pause", command=self.toggle_pause)
        self.pause_resume_button.pack(side='left', padx=5)


        self.randomize_button = ttk.Button(button_frame, text="New Random", command=self.generate_new_random)
        self.randomize_button.pack(side='left', padx=5)

        self.tiles = []
        self.draw_board()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_resume_button.config(text="Resume")
            self.step_button.state(['disabled'])
        else:
            self.pause_resume_button.config(text="Pause")
            self.step_button.state(['!disabled'])

    def get_grid_dimensions(self, grid_size):
        return {
            "3x3": (3, 3),
            "5x5": (5, 5),
            "7x7": (7, 7)
        }.get(grid_size, (3, 3))

    def initialize_puzzle(self):
        print(f"[DEBUG] grid_size = {self.grid_size}, start_type = {self.start_type}")

        # Özel durum (sabit)
        if self.grid_size.lower() == "3x3" and self.start_type.lower() == "special":
            print("[DEBUG] SPECIAL DURUM AKTİF!")
            return [
                [2, 3, 5],
                [0, None, 7],
                [6, 1, 4]
            ]

        # Elle tıklayarak oluşturma
        elif self.start_type.lower() == "manual":
            return [[-1 for _ in range(self.cols)] for _ in range(self.rows)]

        # Dosyadan yükleme
        elif self.start_type.lower() == "fromfile":
            from tkinter import filedialog
            filename = filedialog.askopenfilename(title="Başlangıç Dosyasını Seç", filetypes=[("Text Files", "*.txt")])
            if not filename:
                messagebox.showerror("Hata", "Dosya seçilmedi!")
                return None

            try:
                with open(filename, "r") as f:
                    lines = f.readlines()

                puzzle = []
                for line in lines:
                    row = []
                    for val in line.strip().split():
                        if val == '0':
                            row.append(None)
                        else:
                            row.append(int(val))
                    puzzle.append(row)

                # Grid boyutu kontrolü
                if len(puzzle) != self.rows or any(len(row) != self.cols for row in puzzle):
                    messagebox.showerror("Hata", "Dosyadaki puzzle boyutu seçilen grid ile uyuşmuyor!")
                    return None

                return puzzle

            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}")
                return None

        # Random oluştur
        else:
            size = self.rows * self.cols
            numbers = list(range(size))
            random.shuffle(numbers)

            # 0 -> None dönüşümü garantili ve sadece bir tane
            matrix = [numbers[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]
            none_count = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    if matrix[i][j] == 0:
                        matrix[i][j] = None

            # DEBUG: None kontrolü
            none_count = sum(row.count(None) for row in matrix)
            if none_count != 1:
                print(f"[ERROR] Oluşan puzzle hatalı! None sayısı = {none_count}")
                messagebox.showerror("Hata", f"Puzzle geçersiz. None (boşluk) sayısı: {none_count}")
                return None

            return matrix




    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)

    def draw_board(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.tiles.clear()

        screen_width = self.root.winfo_screenwidth()
        base_size = min(screen_width // (self.cols + 2), 80)
        tile_size = base_size if self.rows <= 3 else base_size * 0.75 if self.rows <= 5 else base_size * 0.6
        font_size = max(10, int(tile_size // 2))

        padding = (self.canvas.winfo_width() - (tile_size * self.cols)) // 2
        if padding < 0:
            padding = 10

        for i in range(self.rows):
            row_tiles = []
            for j in range(self.cols):
                num = self.puzzle_state[i][j]
                text = "" if num is None or num == -1 else str(num)
                tile = tk.Label(
                    self.grid_frame,
                    text=text,
                    font=("Segoe UI", font_size),
                    bg="white",
                    width=3,
                    height=1,
                    borderwidth=2,
                    relief="ridge"
                )

                # Eğer elle dizim modundaysa, kutuya tıklanabilirlik ekle
                if self.start_type.lower() == "manual":
                    tile.bind("<Button-1>", lambda e, x=i, y=j: self.manual_tile_click(x, y))

                tile.grid(row=i, column=j, padx=2, pady=2, ipadx=int(tile_size // 4), ipady=int(tile_size // 4))

            self.tiles.append(row_tiles)

        self.grid_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def find_empty(self, state):
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j] is None:
                    return i, j
        return None

    def get_neighbors(self, state):
        empty_pos = self.find_empty(state)
        if empty_pos is None:
            return []  # boşluk bulunamadıysa komşu üretilemez

        empty_i, empty_j = empty_pos
        neighbors = []
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for move_i, move_j in moves:
            new_i, new_j = empty_i + move_i, empty_j + move_j
            if 0 <= new_i < self.rows and 0 <= new_j < self.cols:
                new_state = [row[:] for row in state]
                new_state[empty_i][empty_j] = new_state[new_i][new_j]
                new_state[new_i][new_j] = None
                neighbors.append(new_state)

        return neighbors


    def state_to_string(self, state):
        return ''.join(str(num if num is not None else '_') for row in state for num in row)

    def cancel_search(self):
        self.cancelled = True
        self.pause_resume_button.state(['disabled'])
        self.step_button.state(['disabled'])
        self.cancel_button.state(['disabled'])
        messagebox.showinfo("Cancel", "Search was cancelled.")

    def manual_tile_click(self, i, j):
        if self.puzzle_state[i][j] != -1:
            return  # zaten doluysa tıklama geçersiz

        next_number = len([n for row in self.puzzle_state for n in row if n != -1])

        if next_number == self.rows * self.cols - 1:
            self.puzzle_state[i][j] = None  # sonuncusu boşluk
        else:
            self.puzzle_state[i][j] = next_number + 1

        self.draw_board()

        # Tüm kutular dolduysa çözüm başlat
        if all(n != -1 for row in self.puzzle_state for n in row):
            messagebox.showinfo("Information", "Puzzle ready, solution begins!")
            self.solution_steps = None  # çözüme hazır
            self.current_step = 0
            self.iteration_count = 0
            self.found_solution = False




    def bfs_solve(self):
        start_state = self.puzzle_state
        queue = deque([(start_state, [])])
        visited = set()

        self.start_time = time.time()  # Çözüm başlangıç zamanı
        self.nodes_expanded = 0  # Expand edilen node sayacı sıfırlanıyor

        while queue:
            current_state, path = queue.popleft()
            state_str = self.state_to_string(current_state)

            if state_str in visited:
                continue

            visited.add(state_str)
            self.nodes_expanded += 1  # Her expand edilen state'de sayaç arttırılıyor

            if self.is_goal_state(current_state):
                self.end_time = time.time()  # Çözüm zamanı durduruluyor
                return path + [current_state]

            for neighbor in self.get_neighbors(current_state):
                if self.state_to_string(neighbor) not in visited:
                    queue.append((neighbor, path + [current_state]))

        self.end_time = time.time()
        return None


    def dfs_solve(self, max_depth=50):
        #DFS algoritması ile çözüm ara (belirli bir derinlik siniriyla)
        start_state = self.puzzle_state
        stack = [(start_state, [], 0)]  # (state, path, depth)
        visited = set()

        self.start_time = time.time()
        self.nodes_expanded = 0

        while stack:
            current_state, path, depth = stack.pop()
            state_str = self.state_to_string(current_state)

            if state_str in visited:
                continue

            visited.add(state_str)
            self.nodes_expanded += 1

            if self.is_goal_state(current_state):
                self.end_time = time.time()
                return path + [current_state]

            if depth < max_depth:
                for neighbor in self.get_neighbors(current_state):
                    if self.state_to_string(neighbor) not in visited:
                        stack.append((neighbor, path + [current_state], depth + 1))

        self.end_time = time.time()
        return None   


    def iterative_deepening_solve(self, max_depth_limit=50):
        """Iterative Deepening DFS algoritması ile çözüm ara"""
        start_state = self.puzzle_state
        self.start_time = time.time()
        self.nodes_expanded = 0

        for depth_limit in range(max_depth_limit + 1):
            stack = [(start_state, [], 0)]
            visited = set()

            while stack:
                current_state, path, depth = stack.pop()
                state_str = self.state_to_string(current_state)

                if state_str in visited:
                    continue

                visited.add(state_str)
                self.nodes_expanded += 1

                if self.is_goal_state(current_state):
                    self.end_time = time.time()
                    return path + [current_state]

                if depth < depth_limit:
                    for neighbor in self.get_neighbors(current_state):
                        if self.state_to_string(neighbor) not in visited:
                            stack.append((neighbor, path + [current_state], depth + 1))

        self.end_time = time.time()
        return None


    def is_goal_state(self, state):
        goal = []
        count = 1
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if i == self.rows-1 and j == self.cols-1:
                    row.append(None)
                else:
                    row.append(count)
                    count += 1
            goal.append(row)
        return state == goal


    def heuristic_misplaced(self, state):
        misplaced = 0
        expected = 1
        for i in range(self.rows):
            for j in range(self.cols):
                if i == self.rows - 1 and j == self.cols - 1:
                    if state[i][j] is not None:
                        misplaced += 1
                else:
                    if state[i][j] != expected:
                        misplaced += 1
                    expected += 1
        return misplaced



    def heuristic_manhattan(self, state):
        distance = 0
        for i in range(self.rows):
            for j in range(self.cols):
                val = state[i][j]
                if val is not None:
                    target_i = (val - 1) // self.cols
                    target_j = (val - 1) % self.cols
                    distance += abs(i - target_i) + abs(j - target_j)
        return distance


    def a_star_solve(self, heuristic_func):
        import heapq
        from itertools import count  # Tie-breaker için
        tie_breaker = count()

        if self.puzzle_state is None:
            messagebox.showerror("HATA", "Puzzle state boş. initialize_puzzle başarısız.")
            print("[FATAL] self.puzzle_state = None")
            return None

        start_state = self.puzzle_state

        print("[A* DEBUG] Başlangıç durumu:")
        for row in start_state:
            print(row)

        h_start = heuristic_func(start_state)
        if h_start is None or not isinstance(h_start, int):
            print(f"[FATAL] Başlangıç heuristic değeri geçersiz: h={h_start}")
            messagebox.showerror("Hata", "Başlangıç heuristic değeri geçersiz.")
            return None

        open_list = []
        heapq.heappush(open_list, (h_start, 0, next(tie_breaker), start_state, []))
        visited = set()

        self.start_time = time.time()
        self.nodes_expanded = 0

        while open_list:
            try:
                f, g, _, current_state, path = heapq.heappop(open_list)
            except Exception as e:
                print(f"[FATAL] heapq.heappop hatası: {e}")
                return None

            state_str = self.state_to_string(current_state)
            if state_str in visited:
                continue

            visited.add(state_str)
            self.nodes_expanded += 1

            if self.is_goal_state(current_state):
                self.end_time = time.time()
                return path + [current_state]

            for neighbor in self.get_neighbors(current_state):
                if neighbor is None:
                    continue

                flat = [item for row in neighbor for item in row]
                if flat.count(None) != 1:
                    print(f"[SKIP] Bozuk state (None sayısı yanlış): {neighbor}")
                    continue

                neighbor_str = self.state_to_string(neighbor)
                if neighbor_str in visited:
                    continue

                h = heuristic_func(neighbor)
                if h is None or not isinstance(h, int):
                    print(f"[SKIP] Geçersiz heuristic değeri: h={h} | state={neighbor}")
                    continue

                try:
                    heapq.heappush(open_list, (g + 1 + h, g + 1, next(tie_breaker), neighbor, path + [current_state]))
                except Exception as e:
                    print(f"[FATAL] HEAPQ push hatası: h={h}, g={g}, neighbor={neighbor}")
                    print("Hata:", e)
                    continue

        self.end_time = time.time()
        return None





    def next_step(self):
        if self.is_paused or self.cancelled:
            return

        if not self.solution_steps:
            if self.algorithm == "BFS":
                self.solution_steps = self.bfs_solve()
            elif self.algorithm == "DFS":
                self.solution_steps = self.dfs_solve()
            elif self.algorithm == "Iterative Deepening":
                self.solution_steps = self.iterative_deepening_solve()
            elif self.algorithm == "A* (Misplaced)":
                self.solution_steps = self.a_star_solve(self.heuristic_misplaced)
            elif self.algorithm == "A* (Manhattan)":
                self.solution_steps = self.a_star_solve(self.heuristic_manhattan)
            else:
                messagebox.showerror("Hata", "Seçilen algoritma henüz desteklenmiyor!")
                return

            if not self.solution_steps:
                messagebox.showinfo("Information", "No solution found!\nYou can use the 'New Random' button to try a new random puzzle.")
                return

            self.current_step = 0

        if self.current_step < len(self.solution_steps):
            self.puzzle_state = self.solution_steps[self.current_step]
            self.draw_board()
            self.current_step += 1
            self.iteration_count += 1
            self.info_label.config(text=f"İterasyon: {self.iteration_count}")
        else:
            if not self.found_solution:
                total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
                messagebox.showinfo(
                    "Successful",
                    f"Solution found!\nTime: {total_time:.4f} seconds\nNumber of nodes expanded: {self.nodes_expanded}"
                )
                self.found_solution = True


    def generate_new_random(self):
        # Yeni geçerli bir random puzzle oluştur
        size = self.rows * self.cols
        numbers = list(range(size))
        random.shuffle(numbers)

        # Matrise çevir
        matrix = [numbers[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                if matrix[i][j] == 0:
                    matrix[i][j] = None

        # Eğer None yoksa garanti ekle
        if not any(None in row for row in matrix):
            matrix[0][0] = None

        self.puzzle_state = matrix

        # Sayaçları sıfırla
        self.solution_steps = None
        self.current_step = 0
        self.iteration_count = 0
        self.found_solution = False
        self.cancelled = False
        self.is_paused = False
        self.info_label.config(text="İterasyon: 0")
        self.pause_resume_button.config(text="Pause")

        # Tahtayı güncelle
        self.draw_board()


