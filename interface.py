import tkinter as tk
import math
import threading
import ctypes
import sys

from tkinter import messagebox
from tkinter import ttk

from config import (
    MODES,
    DIFFICULTIES,
    LEVELS,
    DYNAMIC_SETTINGS,
    MAX_FIELD_SIZE
)

from game import Game
from moving_obstacle import MovingObstacle

class Interface:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("SPACE LANDING")

        self.bg = "#0B1220"
        self.panel = "#172337"
        self.border = "#334155"
        self.text = "#E2E8F0"
        self.muted = "#94A3B8"
        self.cyan = "#38BDF8"
        self.green = "#4ADE80"
        self.yellow = "#FACC15"
        self.red = "#F87171"
        self.purple = "#E879F9"

        self.root.configure(bg=self.bg)

        self.configure_scrollbars()

        self.center_window()

        self.mode = None
        self.difficulty = None
        self.control_mode = "mouse"

        self.width = 20
        self.height = 20

        self.game = None
        self.finished = False

        self.cell_size = 20
        self.origin_x = 0
        self.origin_y = 0

        self.generation_result = None
        self.generation_error = None

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.exit_game
        )

        self.main_menu()

        self.root.update_idletasks()

        self.dark_title_bar(self.root)

        self.root.after(
            50,
            lambda: self.dark_title_bar(self.root)
        )

        self.root.after(
            150,
            lambda: self.dark_title_bar(self.root)
        )

    def configure_scrollbars(self):

        style = ttk.Style(self.root)

        style.theme_use("clam")

        for name in (
            "Dark.Vertical.TScrollbar",
            "Dark.Horizontal.TScrollbar"
        ):

            style.configure(
                name,
                background="#334155",
                troughcolor="#0B1220",
                bordercolor="#0B1220",
                lightcolor="#334155",
                darkcolor="#334155",
                arrowcolor="#94A3B8",
                relief="flat",
                borderwidth=0,
                arrowsize=12,
                gripcount=0,
                width=12
            )

            style.map(
                name,
                background=[
                    ("pressed", "#38BDF8"),
                    ("active", "#475569")
                ],
                arrowcolor=[
                    ("pressed", "#FFFFFF"),
                    ("active", "#38BDF8")
                ],
                lightcolor=[
                    ("pressed", "#38BDF8"),
                    ("active", "#475569")
                ],
                darkcolor=[
                    ("pressed", "#38BDF8"),
                    ("active", "#475569")
                ]
            )

        self.scrollbar_style = style

    def center_window(self):

        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = min(1000, screen_width - 80)
        height = min(600, screen_height - 140)

        x = (screen_width - width) // 2
        y = (screen_height - height - 60) // 2

        self.root.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        self.root.minsize(
            min(900, width),
            min(580, height)
        )

    def dark_title_bar(self, window):

        if sys.platform != "win32":
            return

        if not window.winfo_exists():
            return

        window.update_idletasks()

        user32 = ctypes.windll.user32
        dwm = ctypes.windll.dwmapi

        user32.GetParent.argtypes = [
            ctypes.c_void_p
        ]

        user32.GetParent.restype = ctypes.c_void_p

        hwnd = user32.GetParent(
            window.winfo_id()
        )

        if not hwnd:
            hwnd = window.winfo_id()

        hwnd = ctypes.c_void_p(hwnd)

        dark = ctypes.c_int(1)

        result = dwm.DwmSetWindowAttribute(
            hwnd,
            20,
            ctypes.byref(dark),
            ctypes.sizeof(dark)
        )

        if result != 0:

            dwm.DwmSetWindowAttribute(
                hwnd,
                19,
                ctypes.byref(dark),
                ctypes.sizeof(dark)
            )

        colors = [
            (35, 0x372317),
            (36, 0xF0E8E2),
            (34, 0x554133)
        ]

        for attribute, value in colors:

            color = ctypes.c_uint(value)

            dwm.DwmSetWindowAttribute(
                hwnd,
                attribute,
                ctypes.byref(color),
                ctypes.sizeof(color)
            )

        user32.SetWindowPos(
            hwnd,
            None,
            0, 0, 0, 0,
            0x0037
        )

        user32.SendMessageW(
            hwnd,
            0x0086,
            0,
            0
        )

        user32.SendMessageW(
            hwnd,
            0x0086,
            1,
            0
        )

        user32.RedrawWindow(
            hwnd,
            None,
            None,
            0x0505
        )

        dwm.DwmFlush()

    def run(self):

        self.root.mainloop()

    def clear(self):

        self.root.unbind("<Return>")

        for widget in self.root.winfo_children():

            widget.destroy()
            
    def label(
        self,
        parent,
        text,
        size=12,
        color=None,
        bold=False,
        bg=None,
        **kwargs
    ):

        return tk.Label(
            parent,
            text=text,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            ),
            fg=color or self.text,
            bg=bg or self.bg,
            **kwargs
        )

    def button(
        self,
        parent,
        text,
        command,
        color="#1E3A5F",
        width=28
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            fg=self.text,
            bg=color,
            activebackground="#2563EB",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=width,
            pady=10,
            cursor="hand2"
        )

    def header(self, parent=None):

        parent = parent or self.root

        frame = tk.Frame(
            parent,
            bg=self.bg
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=(12, 8)
        )

        self.label(
            frame,
            "SPACE LANDING",
            28,
            self.cyan,
            True
        ).pack()

        self.label(
            frame,
            "Посадка космічного корабля",
            12,
            self.muted
        ).pack(pady=(0, 10))

        tk.Frame(
            frame,
            bg=self.border,
            height=1
        ).pack(fill="x")

    def title(self, text):

        self.label(
            self.root,
            text,
            19,
            self.cyan,
            True
        ).pack(pady=(5, 12))

    def footer(
        self,
        command,
        text="Назад"
    ):

        frame = tk.Frame(
            self.root,
            bg=self.bg
        )

        frame.pack(
            side="bottom",
            fill="x",
            pady=(8, 18)
        )

        self.button(
            frame,
            text,
            command,
            "#334155",
            32
        ).pack()

        return frame

    def menu_button(
        self,
        parent,
        text,
        command,
        color,
        hover_color,
        border_color,
        text_color
    ):

        width = 280
        height = 42
        radius = 8

        canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=self.panel,
            highlightthickness=0,
            cursor="hand2",
            takefocus=True
        )

        points = [
            radius, 1,
            width - radius, 1,
            width - 1, 1,
            width - 1, radius,
            width - 1, height - radius,
            width - 1, height - 1,
            width - radius, height - 1,
            radius, height - 1,
            1, height - 1,
            1, height - radius,
            1, radius,
            1, 1,
            radius, 1
        ]

        shape = canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            fill=color,
            outline=border_color,
            width=1
        )

        canvas.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 11, "bold")
        )

        def enter(event):

            canvas.itemconfigure(
                shape,
                fill=hover_color
            )

        def leave(event):

            canvas.itemconfigure(
                shape,
                fill=color
            )

        def click(event):

            command()

        canvas.bind("<Enter>", enter)
        canvas.bind("<Leave>", leave)
        canvas.bind("<Button-1>", click)
        canvas.bind("<Return>", click)
        canvas.bind("<space>", click)

        canvas.bind("<FocusIn>", enter)
        canvas.bind("<FocusOut>", leave)

        return canvas

    def main_menu(self):

        self.clear()
        self.header()

        self.label(
            self.root,
            "SPACE LANDING • Космічний симулятор",
            10,
            self.muted
        ).pack(side="bottom", pady=10)

        container = tk.Frame(
            self.root,
            bg=self.bg
        )

        container.pack(
            fill="both",
            expand=True
        )

        card = tk.Frame(
            container,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=650,
            height=370
        )

        canvas = tk.Canvas(
            card,
            width=280,
            height=95,
            bg=self.panel,
            highlightthickness=0
        )

        canvas.pack(pady=(10, 0))

        stars = [
            (20, 20),
            (45, 75),
            (115, 12),
            (155, 85),
            (250, 20),
            (265, 70),
            (180, 10)
        ]

        for x, y in stars:

            canvas.create_oval(
                x, y, x + 2, y + 2,
                fill=self.muted,
                outline=""
            )

        canvas.create_oval(
            190, 10, 264, 84,
            fill="#14532D",
            outline=""
        )

        canvas.create_oval(
            196, 16, 258, 78,
            fill="#22C55E",
            outline="#86EFAC",
            width=2
        )

        canvas.create_oval(
            205, 25, 225, 39,
            fill="#15803D",
            outline=""
        )

        canvas.create_oval(
            232, 48, 250, 63,
            fill="#15803D",
            outline=""
        )

        canvas.create_line(
            85, 62,
            115, 30,
            150, 20,
            190, 43,
            smooth=True,
            fill=self.cyan,
            dash=(4, 5),
            width=2
        )

        canvas.create_polygon(
            64, 57,
            46, 62,
            56, 69,
            fill="#2563EB",
            outline=""
        )

        canvas.create_polygon(
            80, 66,
            78, 84,
            68, 78,
            fill="#2563EB",
            outline=""
        )

        canvas.create_polygon(
            56, 69,
            75, 40,
            98, 29,
            91, 53,
            68, 78,
            fill="#38BDF8",
            outline="#BAE6FD"
        )

        canvas.create_oval(
            76, 43, 87, 54,
            fill="#0B1220",
            outline="#BAE6FD"
        )

        canvas.create_polygon(
            55, 73,
            44, 89,
            64, 79,
            fill="#FACC15",
            outline=""
        )

        self.label(
            card,
            "КОСМІЧНА МІСІЯ",
            23,
            self.cyan,
            True,
            self.panel
        ).pack(pady=(0, 8))

        self.label(
            card,
            "Прокладіть безпечний маршрут до планети,\n"
            "уникаючи астероїдів та небезпечних зон.",
            11,
            self.muted,
            False,
            self.panel,
            justify="center"
        ).pack(pady=(0, 14))

        self.menu_button(
            card,
            "Нова гра",
            self.mode_menu,
            "#164E63",
            "#155E75",
            "#38BDF8",
            "#E0F2FE"
        ).pack(pady=4)

        self.menu_button(
            card,
            "Правила гри",
            self.rules,
            "#1E293B",
            "#334155",
            "#475569",
            "#E2E8F0"
        ).pack(pady=4)

        self.menu_button(
            card,
            "Вихід",
            self.exit_game,
            "#301C26",
            "#4C2530",
            "#9F4545",
            "#FCA5A5"
        ).pack(pady=4)

    def exit_game(self):

        if messagebox.askyesno(
            "Вихід",
            "Ви дійсно бажаєте завершити гру?"
        ):

            self.root.destroy()

    def menu_card(
        self,
        parent,
        title,
        description,
        command,
        color,
        button_text="Обрати"
    ):

        card = tk.Frame(
            parent,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        card.pack_propagate(False)

        self.label(
            card,
            title,
            18,
            color,
            True,
            self.panel
        ).pack(
            padx=10,
            pady=(16, 12)
        )

        button_frame = tk.Frame(
            card,
            bg=self.panel
        )

        button_frame.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=15
        )

        self.button(
            button_frame,
            button_text,
            command,
            "#1D4ED8",
            17
        ).pack(fill="x")

        tk.Frame(
            card,
            bg=self.border,
            height=1
        ).pack(
            side="bottom",
            fill="x",
            padx=15
        )

        content = tk.Frame(
            card,
            bg=self.panel
        )

        content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )

        scrollbar = ttk.Scrollbar(
            content,
            orient="vertical",
            style="Dark.Vertical.TScrollbar"
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        description_box = tk.Text(
            content,
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            padx=8,
            pady=8,
            wrap="word",
            cursor="arrow",
            yscrollcommand=scrollbar.set
        )

        description_box.pack(
            fill="both",
            expand=True
        )

        scrollbar.configure(
            command=description_box.yview
        )

        description_box.insert(
            "1.0",
            description
        )

        description_box.configure(
            state="disabled"
        )

        return card

    def mode_menu(self):

        self.clear()
        self.header()
        self.title("ВИБІР РЕЖИМУ ГРИ")

        self.footer(self.main_menu)

        container = tk.Frame(
            self.root,
            bg=self.bg
        )

        container.pack(
            expand=True,
            fill="both",
            padx=65,
            pady=15
        )

        self.menu_card(
            container,
            "Класичний режим",
            "• До чотирьох перешкод.\n\n"
            "• Нерухомі перешкоди.\n\n"
            "• Необмежена дальність польоту.\n\n"
            "• Стандартні правила гри.",
            lambda: self.select_mode("Класичний"),
            self.green
        )

        self.menu_card(
            container,
            "Розширений режим",
            "• Більше перешкод.\n\n"
            "• Рухомі астероїди.\n\n"
            "• Складні маршрути.\n\n"
            "• Обмежена дальність польоту.\n\n"
            "• Динамічне ігрове середовище.\n\n"
            "• Перешкоди поблизу маршруту.\n\n"
            "• Довші траєкторії астероїдів.",
            lambda: self.select_mode("Розширений"),
            self.yellow
        )

    def select_mode(self, mode):

        self.mode = mode

        self.difficulty_menu()

    def difficulty_menu(self):

        self.clear()
        self.header()
        self.title("РІВЕНЬ СКЛАДНОСТІ")

        self.footer(self.mode_menu)

        self.label(
            self.root,
            f"Обраний режим: {self.mode}",
            13,
            self.muted
        ).pack(pady=5)

        container = tk.Frame(
            self.root,
            bg=self.bg
        )

        container.pack(
            expand=True,
            fill="both",
            padx=25,
            pady=10
        )

        colors = [
            self.green,
            self.yellow,
            self.red
        ]

        for index, difficulty in enumerate(
            DIFFICULTIES.values()
        ):

            (
                count,
                moving,
                sizes,
                radius,
                required,
                minimum
            ) = LEVELS[self.mode][index]

            description = (
                f"Перешкод: {count}\n\n"
                f"Нерухомих: {count - moving}\n\n"
                f"Рухомих: {moving}\n\n"
                f"Розмір перешкод: "
                f"{sizes[0]}–{sizes[1]}\n\n"
            )

            if radius is None:

                description += (
                    "Дальність: необмежена\n\n"
                )

            else:

                description += (
                    f"Дальність: {radius} клітинок\n\n"
                )

            if moving > 0:

                settings = DYNAMIC_SETTINGS[
                    difficulty
                ]

                speed_min, speed_max = settings["speed"]

                travel_min, travel_max = settings["travel"]

                speed = (
                    str(speed_min)
                    if speed_min == speed_max
                    else f"{speed_min}–{speed_max}"
                )

                diagonal = (
                    "Так"
                    if settings["diagonal"]
                    else "Ні"
                )

                description += (
                    f"Швидкість астероїдів: {speed}\n\n"
                    f"Довжина траєкторії: "
                    f"{travel_min}–{travel_max}\n\n"
                    f"Діагональний рух: {diagonal}\n\n"
                )

            description += (
                f"Мінімальне поле: "
                f"{minimum}x{minimum}"
            )

            self.menu_card(
                container,
                difficulty,
                description,
                lambda d=difficulty:
                    self.select_difficulty(d),
                colors[index]
            )

    def select_difficulty(self, difficulty):

        self.difficulty = difficulty

        self.field_menu()

    def get_minimum_size(self):

        index = list(
            DIFFICULTIES.values()
        ).index(self.difficulty)

        return LEVELS[self.mode][index][5]

    def field_menu(self):

        self.clear()
        self.header()
        self.title("РОЗМІР ІГРОВОГО ПОЛЯ")

        self.footer(self.difficulty_menu)

        minimum = self.get_minimum_size()

        self.label(
            self.root,
            f"Режим: {self.mode}    |    "
            f"Складність: {self.difficulty}",
            13,
            self.muted
        ).pack()

        self.label(
            self.root,
            f"Мінімальний розмір: "
            f"{minimum}x{minimum}",
            12,
            self.yellow
        ).pack(pady=10)

        container = tk.Frame(
            self.root,
            bg=self.bg
        )

        container.pack(expand=True)

        for index, size in enumerate(
            range(15, 41, 5)
        ):

            button = self.button(
                container,
                f"{size} × {size}",
                lambda s=size:
                    self.select_field(s, s),
                width=18
            )

            button.grid(
                row=index // 2,
                column=index % 2,
                padx=12,
                pady=10
            )

            if size < minimum:

                button.configure(
                    state="disabled",
                    bg="#1E293B",
                    disabledforeground="#64748B"
                )

        self.button(
            container,
            "Власний розмір поля",
            self.custom_field,
            width=39
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            pady=15
        )

    def custom_field(self):

        self.clear()
        self.header()
        self.title("ВЛАСНИЙ РОЗМІР ПОЛЯ")

        self.footer(self.field_menu)

        minimum = self.get_minimum_size()

        self.label(
            self.root,
            f"Допустимий розмір: "
            f"від {minimum} до {MAX_FIELD_SIZE}",
            13,
            self.muted
        ).pack()

        container = tk.Frame(
            self.root,
            bg=self.panel,
            padx=40,
            pady=25
        )

        container.pack(expand=True)

        self.label(
            container,
            "Ширина поля",
            13,
            bg=self.panel
        ).pack(pady=8)

        width_entry = self.entry(
            container,
            15
        )

        width_entry.pack(ipady=8)

        width_entry.insert(
            0,
            str(minimum)
        )

        self.label(
            container,
            "Висота поля",
            13,
            bg=self.panel
        ).pack(pady=8)

        height_entry = self.entry(
            container,
            15
        )

        height_entry.pack(ipady=8)

        height_entry.insert(
            0,
            str(minimum)
        )

        def confirm():

            try:

                width = int(width_entry.get())

                height = int(height_entry.get())

                if not (
                    minimum <= width <= MAX_FIELD_SIZE
                    and
                    minimum <= height <= MAX_FIELD_SIZE
                ):

                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Помилка",
                    f"Введіть цілі числа "
                    f"від {minimum} до {MAX_FIELD_SIZE}."
                )

                return

            self.select_field(
                width,
                height
            )

        self.button(
            container,
            "Підтвердити",
            confirm,
            "#1D4ED8"
        ).pack(pady=20)

    def entry(self, parent, width=8):

        return tk.Entry(
            parent,
            font=("Segoe UI", 14),
            bg="#0B1220",
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            justify="center",
            width=width,
            highlightthickness=1,
            highlightbackground=self.border,
            highlightcolor=self.cyan
        )

    def select_field(self, width, height):

        self.width = width
        self.height = height

        self.control_menu()

    def control_menu(self):

        self.clear()
        self.header()

        self.title(
            "ВИБІР СПОСОБУ КЕРУВАННЯ"
        )

        self.footer(self.field_menu)

        self.label(
            self.root,
            f"Режим: {self.mode}    |    "
            f"Складність: {self.difficulty}    |    "
            f"Поле: {self.width}x{self.height}",
            12,
            self.muted
        ).pack(pady=10)

        container = tk.Frame(
            self.root,
            bg=self.bg
        )

        container.pack(
            fill="both",
            expand=True,
            padx=65,
            pady=15
        )

        self.menu_card(
            container,
            "Керування мишкою",
            "• Наводьте курсор на клітинку.\n\n"
            "• Переглядайте траєкторію польоту.\n\n"
            "• Натискайте ліву кнопку миші.\n\n"
            "• Корабель переміститься до обраної точки.\n\n"
            "• Координати вводити не потрібно.",
            lambda: self.select_control("mouse"),
            self.cyan
        )

        self.menu_card(
            container,
            "Введення координат",
            "• Вводьте координату X.\n\n"
            "• Вводьте координату Y.\n\n"
            "• Натискайте кнопку «Перемістити» "
            "або клавішу Enter.\n\n"
            "• Корабель переміститься до заданої точки.\n\n"
            "• Натискання на поле не переміщує корабель.",
            lambda: self.select_control("coordinates"),
            self.green
        )

    def select_control(self, control):

        self.control_mode = control

        self.generate_game()

    def control_name(self):

        if self.control_mode == "mouse":

            return "Мишкою"

        return "Координатами"

    def generate_game(self):

        self.clear()
        self.header()

        self.title(
            "ГЕНЕРАЦІЯ ІГРОВОГО ПОЛЯ"
        )

        self.generation_result = None
        self.generation_error = None

        index = list(
            DIFFICULTIES.values()
        ).index(self.difficulty)

        (
            count,
            moving,
            sizes,
            radius,
            required,
            minimum
        ) = LEVELS[self.mode][index]

        container = tk.Frame(
            self.root,
            bg=self.panel,
            padx=45,
            pady=25
        )

        container.pack(expand=True)

        distance = (
            str(radius)
            if radius is not None
            else "Необмежена"
        )

        details = (
            f"Режим: {self.mode}\n\n"
            f"Складність: {self.difficulty}\n\n"
            f"Розмір поля: {self.width}x{self.height}\n\n"
            f"Кількість перешкод: {count}\n\n"
            f"Нерухомих: {count - moving}\n\n"
            f"Рухомих: {moving}\n\n"
            f"Дальність польоту: {distance}\n\n"
            f"Керування: {self.control_name()}"
        )

        self.label(
            container,
            details,
            12,
            bg=self.panel,
            justify="left"
        ).pack()

        self.label(
            container,
            "Генерація поля. Зачекайте...",
            15,
            self.yellow,
            True,
            self.panel
        ).pack(pady=(20, 8))

        self.label(
            container,
            "Перевірка безпечного маршруту...",
            11,
            self.muted,
            False,
            self.panel
        ).pack()

        thread = threading.Thread(
            target=self.create_game,
            daemon=True
        )

        thread.start()

        self.root.after(
            100,
            self.check_generation
        )

    def create_game(self):

        try:

            self.generation_result = Game(
                self.mode,
                self.difficulty,
                self.width,
                self.height
            )

        except Exception as error:

            self.generation_error = str(error)

    def check_generation(self):

        if self.generation_error is not None:

            messagebox.showerror(
                "Помилка генерації",
                self.generation_error
            )

            self.field_menu()

            return

        if self.generation_result is not None:

            self.game = self.generation_result

            self.finished = False

            self.game_screen()

            return

        self.root.after(
            100,
            self.check_generation
        )

    def game_screen(self):

        self.clear()
        self.header()

        self.stats_frame = tk.Frame(
            self.root,
            bg=self.panel
        )

        self.stats_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.stats_label = self.label(
            self.stats_frame,
            "",
            11,
            bg=self.panel,
            justify="left"
        )

        self.stats_label.pack(
            anchor="w",
            padx=12,
            pady=8
        )

        bottom = tk.Frame(
            self.root,
            bg=self.bg
        )

        bottom.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=(5, 10)
        )

        self.create_legend(bottom)

        self.control_frame = tk.Frame(
            bottom,
            bg=self.panel
        )

        self.control_frame.pack(
            fill="x",
            pady=5
        )

        self.status = self.label(
            bottom,
            "Місію розпочато!",
            11,
            self.green,
            True,
            wraplength=850
        )

        self.status.pack(pady=5)

        controls = tk.Frame(
            bottom,
            bg=self.bg
        )

        controls.pack(pady=5)

        self.button(
            controls,
            "Почати заново",
            self.restart_game,
            width=17
        ).pack(
            side="left",
            padx=4
        )

        self.button(
            controls,
            "Змінити поле",
            self.change_field,
            width=17
        ).pack(
            side="left",
            padx=4
        )

        self.button(
            controls,
            "Змінити керування",
            self.change_control,
            width=19
        ).pack(
            side="left",
            padx=4
        )

        self.button(
            controls,
            "Головне меню",
            self.confirm_menu,
            "#334155",
            17
        ).pack(
            side="left",
            padx=4
        )

        self.canvas = tk.Canvas(
            self.root,
            bg="#080E19",
            highlightthickness=1,
            highlightbackground=self.border
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        self.canvas.bind(
            "<Button-1>",
            self.click_cell
        )

        self.canvas.bind(
            "<Motion>",
            self.hover_cell
        )

        self.canvas.bind(
            "<Leave>",
            lambda event:
                self.canvas.delete("hover")
        )

        self.canvas.bind(
            "<Configure>",
            lambda event:
                self.draw_field()
        )

        self.build_control_panel()

        self.update_stats()

        self.root.update_idletasks()

        self.draw_field()

    def build_control_panel(self):

        self.root.unbind("<Return>")

        for widget in self.control_frame.winfo_children():

            widget.destroy()

        if self.control_mode == "mouse":

            self.label(
                self.control_frame,
                "Керування мишкою: натисніть "
                "на потрібну клітинку поля.",
                12,
                self.cyan,
                True,
                self.panel
            ).pack(pady=12)

            return

        container = tk.Frame(
            self.control_frame,
            bg=self.panel
        )

        container.pack(pady=8)

        self.label(
            container,
            "Координата X:",
            11,
            bg=self.panel
        ).pack(
            side="left",
            padx=8
        )

        self.x_entry = self.entry(
            container,
            6
        )

        self.x_entry.pack(
            side="left",
            padx=5,
            ipady=5
        )

        self.label(
            container,
            "Координата Y:",
            11,
            bg=self.panel
        ).pack(
            side="left",
            padx=8
        )

        self.y_entry = self.entry(
            container,
            6
        )

        self.y_entry.pack(
            side="left",
            padx=5,
            ipady=5
        )

        self.button(
            container,
            "Перемістити",
            self.move_by_coordinates,
            "#1D4ED8",
            15
        ).pack(
            side="left",
            padx=12
        )

        self.label(
            self.control_frame,
            f"Допустимі координати: "
            f"X = 0–{self.game.width - 1}, "
            f"Y = 0–{self.game.height - 1}",
            10,
            self.muted,
            bg=self.panel
        ).pack(pady=(0, 8))

        self.root.bind(
            "<Return>",
            lambda event:
                self.move_by_coordinates()
        )

        self.x_entry.focus_set()

    def change_control(self):

        if self.finished:

            return

        window = tk.Toplevel(self.root)

        window.title("Спосіб керування")
        window.geometry("440x300")
        window.resizable(False, False)
        window.configure(bg=self.bg)
        window.transient(self.root)
        window.grab_set()

        self.label(
            window,
            "Оберіть спосіб керування",
            18,
            self.cyan,
            True
        ).pack(pady=20)

        def apply(control):

            self.control_mode = control

            window.destroy()

            self.build_control_panel()

            self.update_stats()

            self.draw_field()

            self.status.configure(
                text=(
                    f"Спосіб керування змінено: "
                    f"{self.control_name()}."
                ),
                fg=self.green
            )

        self.button(
            window,
            "Керування мишкою",
            lambda: apply("mouse"),
            "#1D4ED8"
        ).pack(pady=8)

        self.button(
            window,
            "Введення координат",
            lambda: apply("coordinates"),
            "#1D4ED8"
        ).pack(pady=8)

        self.button(
            window,
            "Скасувати",
            window.destroy,
            "#334155"
        ).pack(pady=8)

    def move_by_coordinates(self):

        if self.finished:

            return

        if self.control_mode != "coordinates":

            return

        try:

            x = int(self.x_entry.get())

            y = int(self.y_entry.get())

        except ValueError:

            self.status.configure(
                text="Помилка! Введіть два цілих числа.",
                fg=self.red
            )

            return

        if self.perform_move(x, y):

            if not self.finished:

                self.x_entry.delete(0, tk.END)

                self.y_entry.delete(0, tk.END)

                self.x_entry.focus_set()

    def create_legend(self, parent):

        container = tk.Frame(
            parent,
            bg=self.bg
        )

        container.pack(pady=4)

        items = [
            ("#38BDF8", "Корабель"),
            ("#22C55E", "Планета"),
            ("#14532D", "Атмосфера"),
            ("#EF4444", "Перешкода"),
            ("#E879F9", "Астероїд"),
            ("#A16207", "Небезпека"),
            ("#164E63", "Дальність")
        ]

        for color, text in items:

            frame = tk.Frame(
                container,
                bg=self.bg
            )

            frame.pack(
                side="left",
                padx=6
            )

            tk.Frame(
                frame,
                bg=color,
                width=12,
                height=12
            ).pack(
                side="left",
                padx=(0, 4)
            )

            self.label(
                frame,
                text,
                10
            ).pack(side="left")

    def update_stats(self):

        game = self.game

        distance = (
            str(game.max_move)
            if game.max_move is not None
            else "Необмежена"
        )

        text = (
            f"Режим: {game.mode}     |     "
            f"Складність: {game.difficulty}     |     "
            f"Ходи: {game.steps}\n"
            f"Поле: {game.width}x{game.height}     |     "
            f"Планета: {game.planet.size}x{game.planet.size}     |     "
            f"Корабель: ({game.ship.x}, {game.ship.y})\n"
            f"Перешкод: {game.count}     |     "
            f"Нерухомих: {game.count - game.moving}     |     "
            f"Рухомих: {game.moving}     |     "
            f"Дальність: {distance}\n"
            f"Керування: {self.control_name()}"
        )

        if game.moving > 0:

            settings = DYNAMIC_SETTINGS[
                game.difficulty
            ]

            speed_min, speed_max = settings["speed"]

            travel_min, travel_max = settings["travel"]

            speed = (
                str(speed_min)
                if speed_min == speed_max
                else f"{speed_min}–{speed_max}"
            )

            diagonal = (
                "Так"
                if settings["diagonal"]
                else "Ні"
            )

            text += (
                f"     |     Швидкість астероїдів: {speed}"
                f"     |     Траєкторія: {travel_min}–{travel_max}"
                f"     |     Діагональний рух: {diagonal}"
            )

        self.stats_label.configure(
            text=text
        )

    def cell_coordinates(self, x, y):

        x1 = (
            self.origin_x
            + x * self.cell_size
        )

        y1 = (
            self.origin_y
            + y * self.cell_size
        )

        return (
            x1,
            y1,
            x1 + self.cell_size,
            y1 + self.cell_size
        )

    def draw_field(self):

        if self.game is None:

            return

        if not hasattr(self, "canvas"):

            return

        if not self.canvas.winfo_exists():

            return

        game = self.game

        canvas = self.canvas

        canvas.delete("all")

        canvas_width = canvas.winfo_width()

        canvas_height = canvas.winfo_height()

        if canvas_width < 50 or canvas_height < 50:

            return

        self.cell_size = max(
            1,
            min(
                (canvas_width - 60) // game.width,
                (canvas_height - 45) // game.height
            )
        )

        field_width = (
            game.width * self.cell_size
        )

        field_height = (
            game.height * self.cell_size
        )

        self.origin_x = (
            canvas_width - field_width
        ) / 2

        self.origin_y = (
            canvas_height - field_height
        ) / 2

        positions = [
            (
                obj,
                obj.at(game.steps)
                if isinstance(obj, MovingObstacle)
                else obj
            )
            for obj in game.obstacles
        ]

        for y in range(game.height):

            for x in range(game.width):

                color = "#0D1726"

                if (
                    not self.finished
                    and game.max_move is not None
                    and math.hypot(
                        x - game.ship.x,
                        y - game.ship.y
                    ) <= game.max_move
                ):

                    color = "#164E63"

                if game.planet.in_atmosphere(x, y):

                    color = "#14532D"

                if game.planet.contains(x, y):

                    color = "#16A34A"

                for obj, position in positions:

                    if position.in_danger_zone(x, y):

                        color = "#59400D"

                    if position.contains(x, y):

                        if isinstance(
                            obj,
                            MovingObstacle
                        ):

                            color = "#86198F"

                        else:

                            color = "#991B1B"

                canvas.create_rectangle(
                    *self.cell_coordinates(x, y),
                    fill=color,
                    outline="#263449",
                    width=1
                )

        font_size = max(
            5,
            min(11, self.cell_size // 2)
        )

        for x in range(game.width):

            canvas.create_text(
                self.origin_x
                + x * self.cell_size
                + self.cell_size / 2,
                self.origin_y - 10,
                text=str(x),
                fill=self.muted,
                font=("Segoe UI", font_size)
            )

        for y in range(game.height):

            canvas.create_text(
                self.origin_x - 15,
                self.origin_y
                + y * self.cell_size
                + self.cell_size / 2,
                text=str(y),
                fill=self.muted,
                font=("Segoe UI", font_size)
            )

        self.draw_planet()

        for obj, position in positions:

            self.draw_obstacle(
                obj,
                position
            )

        self.draw_ship()

        canvas.create_rectangle(
            self.origin_x,
            self.origin_y,
            self.origin_x + field_width,
            self.origin_y + field_height,
            outline=self.cyan,
            width=1
        )

    def draw_planet(self):

        planet = self.game.planet

        size = self.cell_size

        x1 = self.origin_x + planet.x * size

        y1 = self.origin_y + planet.y * size

        x2 = x1 + planet.size * size

        y2 = y1 + planet.size * size

        self.canvas.create_oval(
            x1 + 2,
            y1 + 2,
            x2 - 2,
            y2 - 2,
            fill="#22C55E",
            outline="#86EFAC",
            width=2
        )

        self.canvas.create_oval(
            x1 + (x2 - x1) * 0.2,
            y1 + (y2 - y1) * 0.2,
            x1 + (x2 - x1) * 0.55,
            y1 + (y2 - y1) * 0.45,
            fill="#15803D",
            outline=""
        )

        self.canvas.create_oval(
            x1 + (x2 - x1) * 0.5,
            y1 + (y2 - y1) * 0.55,
            x1 + (x2 - x1) * 0.8,
            y1 + (y2 - y1) * 0.8,
            fill="#15803D",
            outline=""
        )

    def draw_obstacle(self, obj, position):

        size = self.cell_size

        x1 = (
            self.origin_x
            + position.x * size
        )

        y1 = (
            self.origin_y
            + position.y * size
        )

        x2 = x1 + position.size * size

        y2 = y1 + position.size * size

        moving = isinstance(
            obj,
            MovingObstacle
        )

        color = (
            "#A21CAF"
            if moving
            else "#B91C1C"
        )

        outline = (
            self.purple
            if moving
            else self.red
        )

        self.canvas.create_rectangle(
            x1 + 1,
            y1 + 1,
            x2 - 1,
            y2 - 1,
            fill=color,
            outline=outline,
            width=1
        )

        if moving:

            symbol = obj.arrow(
                self.game.steps
            )

            arrows = {
                ">": "→",
                "<": "←",
                "^": "↑",
                "v": "↓"
            }

            symbol = arrows.get(
                symbol,
                symbol
            )

        else:

            symbol = "#"

        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=symbol,
            fill="#FFFFFF",
            font=(
                "Segoe UI Symbol",
                max(6, int(size * 0.8)),
                "bold"
            )
        )

    def draw_ship(self):

        ship = self.game.ship

        x1, y1, x2, y2 = (
            self.cell_coordinates(
                ship.x,
                ship.y
            )
        )

        cx = (x1 + x2) / 2

        cy = (y1 + y2) / 2

        size = self.cell_size

        if not ship.alive:

            self.canvas.create_text(
                cx,
                cy,
                text="✕",
                fill="#FF3333",
                font=(
                    "Segoe UI",
                    max(8, size),
                    "bold"
                )
            )

            return

        self.canvas.create_oval(
            x1 + 1,
            y1 + 1,
            x2 - 1,
            y2 - 1,
            fill="#164E63",
            outline=self.cyan
        )

        self.canvas.create_polygon(
            cx,
            cy - size * 0.42,
            cx - size * 0.32,
            cy + size * 0.30,
            cx,
            cy + size * 0.12,
            cx + size * 0.32,
            cy + size * 0.30,
            fill=self.cyan,
            outline="#BAE6FD"
        )

        self.canvas.create_polygon(
            cx - size * 0.10,
            cy + size * 0.22,
            cx,
            cy + size * 0.43,
            cx + size * 0.10,
            cy + size * 0.22,
            fill="#FB923C",
            outline=""
        )

    def get_clicked_cell(self, event):

        x = math.floor(
            (event.x - self.origin_x)
            / self.cell_size
        )

        y = math.floor(
            (event.y - self.origin_y)
            / self.cell_size
        )

        if not self.game.bounds(x, y):

            return None

        return x, y

    def hover_cell(self, event):

        self.canvas.delete("hover")

        if self.finished:

            return

        cell = self.get_clicked_cell(
            event
        )

        if cell is None:

            return

        x, y = cell

        ship = self.game.ship

        distance = math.hypot(
            x - ship.x,
            y - ship.y
        )

        available = (
            self.game.max_move is None
            or distance <= self.game.max_move
        )

        color = (
            self.cyan
            if available
            else self.red
        )

        x1, y1, x2, y2 = (
            self.cell_coordinates(x, y)
        )

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline=color,
            width=2,
            tags="hover"
        )

        sx1, sy1, sx2, sy2 = (
            self.cell_coordinates(
                ship.x,
                ship.y
            )
        )

        self.canvas.create_line(
            (sx1 + sx2) / 2,
            (sy1 + sy2) / 2,
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            fill=color,
            dash=(4, 4),
            width=2,
            tags="hover"
        )

        self.canvas.create_text(
            self.canvas.winfo_width() - 10,
            10,
            text=f"X: {x}   Y: {y}",
            anchor="ne",
            fill=self.cyan,
            font=("Segoe UI", 10),
            tags="hover"
        )

    def click_cell(self, event):

        if self.finished:

            return

        if self.control_mode != "mouse":

            return

        cell = self.get_clicked_cell(
            event
        )

        if cell is None:

            return

        x, y = cell

        self.perform_move(x, y)

    def perform_move(self, x, y):

        if self.finished:

            return False

        distance = math.hypot(
            x - self.game.ship.x,
            y - self.game.ship.y
        )

        try:

            result = self.game.move(
                x,
                y
            )

        except ValueError as error:

            self.status.configure(
                text=str(error),
                fg=self.red
            )

            return False

        if result == "win":

            self.finished = True

            self.status.configure(
                text="Атмосферу планети досягнуто!",
                fg=self.green
            )

        elif result == "lose":

            self.finished = True

            self.status.configure(
                text="Зіткнення з перешкодою!",
                fg=self.red
            )

        else:

            message = (
                f"Корабель переміщено до ({x}, {y}). "
                f"Відстань: {distance:.2f}."
            )

            if self.game.moving > 0:

                message += (
                    " Астероїди змінили позиції."
                )

            self.status.configure(
                text=message,
                fg=self.green
            )

        self.update_stats()

        self.draw_field()

        if self.finished:

            self.root.unbind("<Return>")

            self.result_window(
                result == "win"
            )

        return True

    def restart_game(self):

        if self.finished or messagebox.askyesno(
            "Нова гра",
            "Згенерувати нове ігрове поле?"
        ):

            self.generate_game()

    def change_field(self):

        if self.finished or messagebox.askyesno(
            "Розмір поля",
            "Завершити поточну місію та змінити поле?"
        ):

            self.field_menu()

    def confirm_menu(self):

        if self.finished or messagebox.askyesno(
            "Головне меню",
            "Повернутися до головного меню?"
        ):

            self.main_menu()

    def result_window(self, victory):

        window = tk.Toplevel(self.root)
        window.withdraw()

        window.title("Результат космічної місії")
        window.configure(bg=self.bg)
        window.resizable(False, False)
        window.transient(self.root)

        game = self.game

        color = self.green if victory else self.red

        title = (
            "МІСІЮ ВИКОНАНО!"
            if victory
            else "МІСІЮ ПРОВАЛЕНО!"
        )

        description = (
            "Корабель успішно досяг атмосфери планети."
            if victory
            else "Космічний корабель зруйновано."
        )

        container = tk.Frame(
            window,
            bg=self.bg
        )

        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=16
        )

        header = tk.Frame(
            container,
            bg=self.bg
        )

        header.pack(fill="x")

        self.label(
            header,
            "✓" if victory else "✕",
            30,
            color,
            True
        ).pack()

        self.label(
            header,
            title,
            23,
            color,
            True
        ).pack(pady=(0, 5))

        self.label(
            header,
            description,
            11,
            self.muted
        ).pack()

        tk.Frame(
            container,
            bg=self.border,
            height=1
        ).pack(
            fill="x",
            pady=12
        )

        metrics = tk.Frame(
            container,
            bg=self.bg
        )

        metrics.pack(fill="x")

        cards = [
            (
                str(game.steps),
                "Виконано ходів",
                self.cyan
            )
        ]

        if victory and game.minimum_steps is not None:

            difference = (
                game.steps - game.minimum_steps
            )

            cards.extend([
                (
                    str(game.minimum_steps),
                    "Оптимальна кількість",
                    self.green
                ),
                (
                    f"+{difference}" if difference > 0
                    else str(difference),
                    "Додаткові ходи",
                    self.yellow
                )
            ])

        else:

            cards.extend([
                (
                    str(game.count),
                    "Перешкод",
                    self.yellow
                ),
                (
                    str(game.moving),
                    "Рухомих астероїдів",
                    self.purple
                )
            ])

        for index, (value, name, card_color) in enumerate(cards):

            metrics.grid_columnconfigure(
                index,
                weight=1,
                uniform="metrics"
            )

            card = tk.Frame(
                metrics,
                bg=self.panel,
                highlightbackground=self.border,
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=4
            )

            self.label(
                card,
                value,
                25,
                card_color,
                True,
                self.panel
            ).pack(pady=(7, 0))

            self.label(
                card,
                name,
                10,
                self.muted,
                False,
                self.panel
            ).pack(pady=(0, 9))

        statistics = tk.Frame(
            container,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        statistics.pack(
            fill="x",
            pady=12
        )

        self.label(
            statistics,
            "СТАТИСТИКА МІСІЇ",
            12,
            self.cyan,
            True,
            self.panel
        ).pack(pady=(9, 5))

        details_frame = tk.Frame(
            statistics,
            bg=self.panel
        )

        details_frame.pack(
            fill="x",
            padx=14,
            pady=(0, 10)
        )

        details_frame.grid_columnconfigure(
            0,
            weight=1
        )

        details_frame.grid_columnconfigure(
            1,
            weight=1
        )

        details = [
            ("Режим", game.mode),
            ("Складність", game.difficulty),
            ("Розмір поля", f"{game.width} × {game.height}"),
            ("Кількість перешкод", game.count),
            ("Нерухомих", game.count - game.moving),
            ("Рухомих", game.moving),
            ("Керування", self.control_name()),
            ("Результат", "Перемога" if victory else "Поразка")
        ]

        for index, (name, value) in enumerate(details):

            item = tk.Frame(
                details_frame,
                bg=self.panel
            )

            item.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=8,
                pady=4
            )

            self.label(
                item,
                f"{name}:",
                10,
                self.muted,
                False,
                self.panel
            ).pack(side="left")

            self.label(
                item,
                str(value),
                10,
                self.text,
                True,
                self.panel
            ).pack(side="right")

        if (
            victory
            and game.minimum_steps is not None
            and game.steps == game.minimum_steps
        ):

            self.label(
                container,
                "Ви обрали найкоротший маршрут!",
                11,
                self.green,
                True
            ).pack(pady=(0, 6))

        def navigate(command):

            window.grab_release()
            window.destroy()

            command()

        buttons = tk.Frame(
            container,
            bg=self.bg
        )

        buttons.pack(fill="x")

        buttons.grid_columnconfigure(
            0,
            weight=1,
            uniform="buttons"
        )

        buttons.grid_columnconfigure(
            1,
            weight=1,
            uniform="buttons"
        )

        replay = self.button(
            buttons,
            "Зіграти ще раз",
            lambda: navigate(self.generate_game),
            "#1D4ED8"
        )

        replay.configure(
            font=("Segoe UI", 11, "bold"),
            pady=9
        )

        replay.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=4,
            pady=4
        )

        options = [
            (
                "Змінити розмір поля",
                self.field_menu
            ),
            (
                "Змінити складність",
                self.difficulty_menu
            ),
            (
                "Змінити режим гри",
                self.mode_menu
            ),
            (
                "Головне меню",
                self.main_menu
            )
        ]

        for index, (text, command) in enumerate(options):

            button = self.button(
                buttons,
                text,
                lambda c=command: navigate(c),
                "#1E3A5F"
            )

            button.configure(
                font=("Segoe UI", 10, "bold"),
                pady=7
            )

            button.grid(
                row=index // 2 + 1,
                column=index % 2,
                sticky="ew",
                padx=4,
                pady=4
            )

        window.update_idletasks()
        self.root.update_idletasks()

        width = max(
            680,
            window.winfo_reqwidth()
        )

        height = window.winfo_reqheight() + 10

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = self.root.winfo_rootx() + (
            self.root.winfo_width() - width
        ) // 2

        y = self.root.winfo_rooty() + (
            self.root.winfo_height() - height
        ) // 2

        x = max(
            10,
            min(x, screen_width - width - 10)
        )

        y = max(
            10,
            min(y, screen_height - height - 80)
        )

        window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        window.deiconify()
        window.update_idletasks()
        window.lift()
        window.grab_set()
        window.focus_force()

        self.dark_title_bar(window)

        window.after(
            50,
            lambda: self.dark_title_bar(window)
        )

        window.after(
            150,
            lambda: self.dark_title_bar(window)
        )
        
    def rules(self):

        self.clear()
        self.header()
        self.title("ПРАВИЛА ГРИ")

        self.footer(
            self.main_menu,
            "Повернутися до головного меню"
        )

        container = tk.Frame(
            self.root,
            bg=self.panel
        )

        container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=5
        )

        scrollbar = tk.Scrollbar(
            container
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        text = tk.Text(
            container,
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 12),
            relief="flat",
            padx=25,
            pady=20,
            wrap="word",
            yscrollcommand=scrollbar.set
        )

        text.pack(
            fill="both",
            expand=True
        )

        scrollbar.configure(
            command=text.yview
        )

        text.tag_configure(
            "title",
            foreground=self.cyan,
            font=("Segoe UI", 17, "bold")
        )

        text.tag_configure(
            "green",
            foreground=self.green,
            font=("Segoe UI", 13, "bold")
        )

        text.tag_configure(
            "yellow",
            foreground=self.yellow,
            font=("Segoe UI", 13, "bold")
        )

        text.tag_configure(
            "red",
            foreground=self.red,
            font=("Segoe UI", 13, "bold")
        )

        text.tag_configure(
            "purple",
            foreground=self.purple,
            font=("Segoe UI", 13, "bold")
        )

        sections = [

            (
                "ОСНОВНА МЕТА\n",
                "title"
            ),

            (
                "Керуйте космічним кораблем та досягніть "
                "атмосфери планети, уникаючи перешкод "
                "та небезпечних зон.\n\n",
                None
            ),

            (
                "КЕРУВАННЯ КОРАБЛЕМ\n",
                "title"
            ),

            (
                "1. Оберіть режим гри.\n"
                "2. Оберіть рівень складності.\n"
                "3. Виберіть розмір ігрового поля.\n"
                "4. Оберіть спосіб керування кораблем.\n"
                "5. Переміщуйте корабель до планети.\n"
                "6. Уникайте перешкод та небезпечних зон.\n"
                "7. Досягніть атмосфери планети.\n\n",
                None
            ),

            (
                "КЕРУВАННЯ МИШКОЮ\n",
                "title"
            ),

            (
                "Наведіть курсор на потрібну клітинку.\n"
                "Пунктирна лінія показує траєкторію польоту.\n"
                "Натисніть ліву кнопку миші для переміщення.\n"
                "Координати вводити не потрібно.\n\n",
                None
            ),

            (
                "КЕРУВАННЯ КООРДИНАТАМИ\n",
                "title"
            ),

            (
                "Введіть координату X у відповідне поле.\n"
                "Введіть координату Y у відповідне поле.\n"
                "Натисніть кнопку «Перемістити» або Enter.\n"
                "Координати повинні бути цілими числами.\n"
                "Координати не повинні виходити за межі поля.\n\n"
                "У цьому режимі натискання на ігрове поле "
                "не переміщує корабель.\n\n"
                "Спосіб керування можна змінити під час гри "
                "кнопкою «Змінити керування».\n\n",
                None
            ),

            (
                "УМОВИ ПЕРЕМОГИ ТА ПОРАЗКИ\n",
                "title"
            ),

            (
                "Перемога настає, коли корабель досягає "
                "атмосфери планети.\n\n"
                "Поразка настає, якщо корабель потрапляє "
                "на перешкоду або в її небезпечну зону.\n\n"
                "Корабель рухається по прямій лінії.\n"
                "Перевіряється вся траєкторія польоту, "
                "а не лише кінцева точка переміщення.\n\n",
                None
            ),

            (
                "КЛАСИЧНИЙ РЕЖИМ\n",
                "green"
            ),

            (
                "До чотирьох нерухомих перешкод.\n"
                "Дальність польоту необмежена.\n"
                "Розмір планети: від 4x4 до 5x5.\n"
                "Розмір перешкод: від 1x1 до 3x3.\n"
                "Відстань між перешкодами: від 3 клітинок.\n\n",
                None
            ),

            (
                "Легка складність\n",
                "green"
            ),

            (
                "Перешкод: 2.\n"
                "Дальність польоту: необмежена.\n\n",
                None
            ),

            (
                "Середня складність\n",
                "yellow"
            ),

            (
                "Перешкод: 3.\n"
                "Дальність польоту: необмежена.\n\n",
                None
            ),

            (
                "Важка складність\n",
                "red"
            ),

            (
                "Перешкод: 4.\n"
                "Дальність польоту: необмежена.\n\n",
                None
            ),

            (
                "РОЗШИРЕНИЙ РЕЖИМ\n",
                "yellow"
            ),

            (
                "Більша кількість перешкод.\n"
                "Рухомі астероїди.\n"
                "Обмежена дальність польоту.\n"
                "Складніші маршрути до планети.\n"
                "Перешкоди поблизу маршруту корабля.\n"
                "Довгі траєкторії руху астероїдів.\n\n",
                None
            ),

            (
                "Легка складність\n",
                "green"
            ),

            (
                "Перешкод: 4.\n"
                "Нерухомих: 4.\n"
                "Рухомих: 0.\n"
                "Дальність польоту: необмежена.\n\n",
                None
            ),

            (
                "Середня складність\n",
                "yellow"
            ),

            (
                "Перешкод: 6.\n"
                "Нерухомих: 4.\n"
                "Рухомих: 2.\n"
                "Дальність польоту: 5 клітинок.\n"
                "Швидкість астероїдів: 1 клітинка.\n"
                "Довжина траєкторії: 3–5 клітинок.\n"
                "Горизонтальний та вертикальний рух.\n\n",
                None
            ),

            (
                "Важка складність\n",
                "red"
            ),

            (
                "Перешкод: 9.\n"
                "Нерухомих: 5.\n"
                "Рухомих: 4.\n"
                "Дальність польоту: 3 клітинки.\n"
                "Швидкість астероїдів: 1–2 кроки.\n"
                "Довжина траєкторії: 4–7 кроків.\n"
                "Горизонтальний, вертикальний "
                "та діагональний рух.\n\n",
                None
            ),

            (
                "РУХОМІ ПЕРЕШКОДИ\n",
                "purple"
            ),

            (
                "Астероїди переміщуються після кожного "
                "правильного ходу космічного корабля.\n\n"
                "Напрямок руху показується стрілками:\n\n"
                "→ — Праворуч\n"
                "← — Ліворуч\n"
                "↑ — Вгору\n"
                "↓ — Вниз\n"
                "↗ — Вгору праворуч\n"
                "↖ — Вгору ліворуч\n"
                "↘ — Вниз праворуч\n"
                "↙ — Вниз ліворуч\n\n"
                "Астероїди рухаються вздовж траєкторії "
                "протягом декількох ходів.\n\n"
                "Після досягнення кінця траєкторії "
                "астероїд змінює напрямок руху.\n\n"
                "Якщо астероїд або його небезпечна зона "
                "перетинає позицію корабля, місію провалено.\n\n"
                "Недопустимі переміщення корабля "
                "не спричиняють руху астероїдів.\n\n"
                "Зміна способу керування не витрачає хід.\n\n"
                "Кожне поле перевіряється на наявність "
                "безпечного маршруту до планети.\n\n",
                None
            ),

            (
                "ПОЗНАЧЕННЯ ІГРОВИХ ОБ'ЄКТІВ\n",
                "title"
            ),

            (
                "Блакитний корабель — гравець.\n"
                "Зелена планета — ціль місії.\n"
                "Темно-зелена зона — атмосфера планети.\n"
                "Червоні блоки — нерухомі перешкоди.\n"
                "Фіолетові блоки — рухомі астероїди.\n"
                "Жовті клітинки — небезпечна зона.\n"
                "Блакитні клітинки — дальність польоту.\n"
                "Темні клітинки — вільний простір.\n"
                "Червоний хрест — зруйнований корабель.\n\n"
                "Підсвічування дальності не гарантує "
                "безпечної траєкторії польоту.\n",
                None
            )
        ]

        for content, tag in sections:

            if tag:

                text.insert(
                    "end",
                    content,
                    tag
                )

            else:

                text.insert(
                    "end",
                    content
                )

        text.configure(
            state="disabled"
        )