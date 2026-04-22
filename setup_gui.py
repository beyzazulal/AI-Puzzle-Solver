import tkinter as tk
from tkinter import ttk, messagebox

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", 
                         relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class SetupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Puzzle Solver - Kurulum Ekranı")

        # Ekranı tam ekran yap
        self.root.state('zoomed')  # Windows için tam ekran
        self.root.configure(bg="#e6e6e6")

        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Segoe UI', 14), background="#e6e6e6")
        style.configure('TButton', font=('Segoe UI', 13))
        style.configure('TCombobox', font=('Segoe UI', 13))
        style.configure('TRadiobutton', font=('Segoe UI', 13))

        style.configure('Custom.TFrame', background='#e6e6e6')
        style.configure('Custom.TButton',
                        background='#4a90e2',
                        foreground='white',
                        padding=(10, 5),
                        font=('Segoe UI', 13, 'bold'))

        # Başlık
        title = tk.Label(root, text="Artificial Intelligence Puzzle Solver - Initial Settings", 
                         font=("Segoe UI", 26, "bold"), bg="#e6e6e6", fg="#333")
        title.pack(pady=30)

        # Ana çerçeve
        frame = ttk.Frame(root, padding=40, style='Custom.TFrame')
        frame.pack(expand=True)

        # Izgara boyutu
        ttk.Label(frame, text="Grid Size:").grid(row=0, column=0, padx=15, pady=15, sticky="e")
        self.grid_size_var = tk.StringVar(value="3x3")
        grid_options = ["3x3", "5x5", "7x7"]
        self.grid_menu = ttk.Combobox(frame, textvariable=self.grid_size_var, values=grid_options, state="readonly", width=25)
        self.grid_menu.grid(row=0, column=1, sticky="w")

        # Algoritma seçimi
        ttk.Label(frame, text="Algorithm Selection:").grid(row=1, column=0, padx=15, pady=15, sticky="e")
        self.algorithm_var = tk.StringVar(value="BFS")
        algo_options = ["BFS", "DFS", "Iterative Deepening", "A* (Misplaced)", "A* (Manhattan)"]
        self.algo_menu = ttk.Combobox(frame, textvariable=self.algorithm_var, values=algo_options, state="readonly", width=25)
        self.algo_menu.grid(row=1, column=1, sticky="w")

        # Başlangıç türü
        ttk.Label(frame, text="Start Type:").grid(row=2, column=0, padx=15, pady=15, sticky="ne")
        self.start_type_var = tk.StringVar(value="Random")
        self.start_random_rb = ttk.Radiobutton(frame, text="Random", variable=self.start_type_var, value="Random")
        self.start_special_rb = ttk.Radiobutton(frame, text="Special (2 3 5 / 0 7 / 6 1 4)", variable=self.start_type_var, value="Special")
        self.start_file_rb = ttk.Radiobutton(frame, text="Load from File", variable=self.start_type_var, value="FromFile")
        
        self.start_file_rb.grid(row=4, column=1, sticky="w", pady=5)
        self.start_random_rb.grid(row=2, column=1, sticky="w", pady=5)
        self.start_special_rb.grid(row=3, column=1, sticky="w", pady=5)

        self.start_manual_rb = ttk.Radiobutton(frame, text="Create by Hand (By clicking)", variable=self.start_type_var, value="Manual")
        self.start_manual_rb.grid(row=5, column=1, sticky="w", pady=5)

        # Izgara seçimi değişince başlangıç seçeneklerini kontrol et
        self.grid_menu.bind("<<ComboboxSelected>>", self.update_start_options)

        # Başlat butonu
        self.start_button = ttk.Button(root, text="Start", command=self.start_game, style='Custom.TButton')
        self.start_button.pack(pady=40)

        # Tooltipler
        self.create_tooltips()

    def create_tooltips(self):
        Tooltip(self.grid_menu, "Select the grid size for the puzzle")
        Tooltip(self.algo_menu, "Select the algorithm to be used for the solution")

    def update_start_options(self, event=None):
        if self.grid_size_var.get() == "3x3":
            self.start_random_rb.state(["!disabled"])
            self.start_special_rb.state(["!disabled"])
        else:
            self.start_random_rb.state(["!disabled"])
            self.start_special_rb.state(["disabled"])
            self.start_type_var.set("Random")

    def start_game(self):
        grid = self.grid_size_var.get()
        algo = self.algorithm_var.get()
        start_type = self.start_type_var.get()

        if grid != "3x3" and start_type == "Special":
            messagebox.showerror("Hata", "Özel başlangıç sadece 3x3 için geçerlidir.")
            return

        elif start_type not in ["Random", "Special", "Manual", "FromFile"]:
            messagebox.showerror("Hata", "Bilinmeyen başlangıç tipi!")
            return


        # İlk pencereyi kapat
        self.root.destroy()

        # Yeni ekranı başlat
        import solver_gui
        solver_gui.launch_solver(grid, algo, start_type)

if __name__ == "__main__":
    root = tk.Tk()  # Changed from tix to tk
    app = SetupGUI(root)
    root.mainloop()
