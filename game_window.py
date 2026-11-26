import tkinter as tk
import math

from tkinter import messagebox

from interface import Interface
from config import DYNAMIC_SETTINGS
from moving_obstacle import MovingObstacle
from tkinter import ttk


class GameWindow(Interface):

    def __init__(self):

        self.game_window = None
        self.menu_root = None
        self.zoom = 1.0
        self.base_cell_size = 20

        super().__init__()

        self.menu_root = self.root

    def clear(self):

        if self.game_window is not None:

            self.game_window.destroy()
            self.game_window = None

            self.restore_menu_window()

        super().clear()

    def game_screen(self):

        self.clear()

        self.menu_root = self.root

        self.menu_root.update_idletasks()

        self.saved_menu_state = self.menu_root.state()
        self.saved_menu_geometry = self.menu_root.geometry()

        self.game_window = tk.Toplevel(
            self.menu_root
        )

        self.root = self.game_window

        self.root.title(
            "SPACE LANDING — Космічна місія"
        )

        self.root.configure(bg=self.bg)

        self.root.minsize(950, 600)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.confirm_menu
        )

        self.menu_root.withdraw()

        try:

            self.root.state("zoomed")

        except tk.TclError:

            self.root.geometry(
                f"{self.root.winfo_screenwidth()}x"
                f"{self.root.winfo_screenheight()}+0+0"
            )

        self.zoom = 1.0
        self.base_cell_size = 20

        self.create_game_header()

        content = tk.Frame(
            self.root,
            bg=self.bg
        )

        content.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        sidebar_container = tk.Frame(
            content,
            bg=self.panel,
            width=370,
            highlightbackground=self.border,
            highlightthickness=1
        )

        sidebar_container.pack(
            side="right",
            fill="y",
            padx=(12, 0)
        )

        sidebar_container.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(
            sidebar_container,
            bg=self.panel,
            highlightthickness=0,
            bd=0
        )

        sidebar_scrollbar = ttk.Scrollbar(
            sidebar_container,
            orient="vertical",
            command=self.sidebar_canvas.yview,
            style="Dark.Vertical.TScrollbar"
        )

        sidebar_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.sidebar_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.sidebar_canvas.configure(
            yscrollcommand=sidebar_scrollbar.set
        )

        self.sidebar = tk.Frame(
            self.sidebar_canvas,
            bg=self.panel
        )

        sidebar_window = self.sidebar_canvas.create_window(
            (0, 0),
            window=self.sidebar,
            anchor="nw"
        )

        def update_scrollregion(event=None):

            self.sidebar_canvas.configure(
                scrollregion=self.sidebar_canvas.bbox("all")
            )

        def resize_sidebar(event):

            self.sidebar_canvas.itemconfigure(
                sidebar_window,
                width=event.width
            )

        self.sidebar.bind(
            "<Configure>",
            update_scrollregion
        )

        self.sidebar_canvas.bind(
            "<Configure>",
            resize_sidebar
        )

        def scroll_sidebar(event):

            self.sidebar_canvas.yview_scroll(
                -int(event.delta / 120),
                "units"
            )

            return "break"

        def bind_sidebar_scroll(widget):

            widget.bind(
                "<MouseWheel>",
                scroll_sidebar
            )

            for child in widget.winfo_children():

                bind_sidebar_scroll(child)

        map_container = tk.Frame(
            content,
            bg=self.bg
        )

        map_container.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.create_map(map_container)

        self.create_sidebar()

        self.build_control_panel()

        self.update_stats()

        bind_sidebar_scroll(self.sidebar)
        bind_sidebar_scroll(self.sidebar_canvas)

        self.root.update_idletasks()

        update_scrollregion()

        self.fit_map()

        self.dark_title_bar(self.root)

    def restore_menu_window(self):

        self.root = self.menu_root

        self.root.deiconify()

        if self.saved_menu_state == "zoomed":

            self.root.state("zoomed")

        else:

            self.root.state("normal")

            self.root.geometry(
                self.saved_menu_geometry
            )

        self.root.lift()

        self.root.focus_force()

        self.root.update_idletasks()

        self.dark_title_bar(self.root)

    def create_game_header(self):

        header = tk.Frame(
            self.root,
            bg=self.bg
        )

        header.pack(
            fill="x",
            padx=15,
            pady=8
        )

        self.label(
            header,
            "SPACE LANDING",
            23,
            self.cyan,
            True
        ).pack(side="left")

        self.label(
            header,
            "Посадка космічного корабля",
            12,
            self.muted
        ).pack(
            side="left",
            padx=20
        )

        self.button(
            header,
            "Головне меню",
            self.confirm_menu,
            "#334155",
            17
        ).pack(side="right")

    def create_map(self, parent):

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            parent,
            bg="#080E19",
            highlightthickness=1,
            highlightbackground=self.border
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.canvas.yview,
            style="Dark.Vertical.TScrollbar"
        )

        vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal = ttk.Scrollbar(
            parent,
            orient="horizontal",
            command=self.canvas.xview,
            style="Dark.Horizontal.TScrollbar"
        )

        horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        corner = tk.Frame(
            parent,
            bg=self.bg
        )

        corner.grid(
            row=1,
            column=1,
            sticky="nsew"
        )

        self.canvas.configure(
            xscrollcommand=horizontal.set,
            yscrollcommand=vertical.set
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

        self.canvas.bind(
            "<MouseWheel>",
            self.mouse_zoom
        )

        self.canvas.bind(
            "<Button-4>",
            lambda event:
                self.change_zoom(0.1)
        )

        self.canvas.bind(
            "<Button-5>",
            lambda event:
                self.change_zoom(-0.1)
        )

        self.canvas.bind(
            "<ButtonPress-3>",
            self.start_pan
        )

        self.canvas.bind(
            "<B3-Motion>",
            self.move_pan
        )

        self.label(
            parent,
            "Коліщатко — масштабування  |  "
            "Права кнопка миші — переміщення карти",
            10,
            self.muted
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=5
        )

    def create_sidebar(self):

        self.label(
            self.sidebar,
            "ІНФОРМАЦІЯ ПРО МІСІЮ",
            14,
            self.cyan,
            True,
            self.panel
        ).pack(pady=(10, 5))

        self.create_separator(
            self.sidebar
        )

        self.stats_label = self.label(
            self.sidebar,
            "",
            10,
            bg=self.panel,
            justify="left",
            anchor="w"
        )

        self.stats_label.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.create_separator(
            self.sidebar
        )

        self.create_zoom_panel()

        self.create_separator(
            self.sidebar
        )

        self.control_frame = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        self.control_frame.pack(
            fill="x",
            padx=10,
            pady=3
        )

        self.status = self.label(
            self.sidebar,
            "Місію розпочато!",
            10,
            self.green,
            True,
            self.panel,
            wraplength=300,
            justify="center"
        )

        self.status.pack(
            fill="x",
            padx=10,
            pady=8
        )

        navigation = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        navigation.pack(
            fill="x",
            padx=12,
            pady=(5, 10)
        )

        navigation.grid_columnconfigure(
            0,
            weight=1,
            uniform="navigation"
        )

        navigation.grid_columnconfigure(
            1,
            weight=1,
            uniform="navigation"
        )

        restart_button = self.button(
            navigation,
            "Почати заново",
            self.restart_game,
            "#1D4ED8",
            20
        )

        restart_button.configure(
            font=("Segoe UI", 11, "bold"),
            height=1,
            pady=12
        )

        restart_button.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 6)
        )

        options = [
            (
                "Змінити керування",
                self.change_control,
                "#1E3A5F"
            ),
            (
                "Змінити поле",
                self.change_field,
                "#1E3A5F"
            )
        ]

        for index, (text, command, color) in enumerate(options):

            button = self.button(
                navigation,
                text,
                command,
                color,
                15
            )

            button.configure(
                font=("Segoe UI", 9, "bold"),
                height=1,
                pady=8
            )

            button.grid(
                row=1,
                column=index,
                sticky="ew",
                padx=2,
                pady=3
            )

        menu_button = self.button(
            navigation,
            "Головне меню",
            self.confirm_menu,
            "#334155",
            20
        )

        menu_button.configure(
            font=("Segoe UI", 10, "bold"),
            height=1,
            pady=8
        )

        menu_button.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(5, 0)
        )

        self.create_separator(
            self.sidebar
        )

        self.create_legend(
            self.sidebar
        )

    def create_separator(self, parent):

        tk.Frame(
            parent,
            bg=self.border,
            height=1
        ).pack(
            fill="x",
            padx=12,
            pady=5
        )

    def create_zoom_panel(self):

        self.label(
            self.sidebar,
            "МАСШТАБ КАРТИ",
            12,
            self.cyan,
            True,
            self.panel
        ).pack(pady=4)

        container = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        container.pack(pady=5)

        self.button(
            container,
            "−",
            lambda:
                self.change_zoom(-0.1),
            width=4
        ).pack(
            side="left",
            padx=4
        )

        self.zoom_label = self.label(
            container,
            "100%",
            13,
            self.text,
            True,
            self.panel,
            width=7
        )

        self.zoom_label.pack(
            side="left",
            padx=4
        )

        self.button(
            container,
            "+",
            lambda:
                self.change_zoom(0.1),
            width=4
        ).pack(
            side="left",
            padx=4
        )

        buttons = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        buttons.pack(
            fill="x",
            padx=12,
            pady=4
        )

        fit_button = self.button(
            buttons,
            "Вмістити",
            self.fit_map,
            "#334155",
            10
        )

        fit_button.configure(pady=5)

        fit_button.pack(
            side="left",
            expand=True,
            fill="x",
            padx=3
        )

        reset_button = self.button(
            buttons,
            "100%",
            self.reset_zoom,
            "#334155",
            10
        )

        reset_button.configure(pady=5)

        reset_button.pack(
            side="left",
            expand=True,
            fill="x",
            padx=3
        )

    def fit_map(self):

        if self.game is None:
            return

        self.root.update_idletasks()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        fitted_size = min(
            (width - 50) / self.game.width,
            (height - 50) / self.game.height
        )

        self.zoom = max(
            0.4,
            min(3.0, fitted_size / self.base_cell_size)
        )

        self.update_zoom()

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def reset_zoom(self):

        self.zoom = 1.0

        self.update_zoom()

    def change_zoom(self, amount):

        self.zoom = round(
            max(
                0.4,
                min(
                    3.0,
                    self.zoom + amount
                )
            ),
            2
        )

        self.update_zoom()

    def update_zoom(self):

        if hasattr(self, "zoom_label"):

            if self.zoom_label.winfo_exists():

                self.zoom_label.configure(
                    text=f"{int(self.zoom * 100)}%"
                )

        self.draw_field()

    def mouse_zoom(self, event):

        if event.delta > 0:

            self.change_zoom(0.1)

        else:

            self.change_zoom(-0.1)

        return "break"

    def start_pan(self, event):

        self.canvas.scan_mark(
            event.x,
            event.y
        )

    def move_pan(self, event):

        self.canvas.scan_dragto(
            event.x,
            event.y,
            gain=1
        )

    def build_control_panel(self):

        self.root.unbind("<Return>")

        for widget in self.control_frame.winfo_children():

            widget.destroy()

        self.label(
            self.control_frame,
            "КЕРУВАННЯ КОРАБЛЕМ",
            12,
            self.cyan,
            True,
            self.panel
        ).pack(pady=4)

        if self.control_mode == "mouse":

            self.label(
                self.control_frame,
                "Натисніть на потрібну "
                "клітинку карти.",
                10,
                self.text,
                False,
                self.panel,
                wraplength=260,
                justify="center"
            ).pack(pady=5)

            return

        coordinates = tk.Frame(
            self.control_frame,
            bg=self.panel
        )

        coordinates.pack(pady=5)

        self.label(
            coordinates,
            "X:",
            12,
            bg=self.panel
        ).pack(
            side="left",
            padx=5
        )

        self.x_entry = self.entry(
            coordinates,
            5
        )

        self.x_entry.pack(
            side="left",
            padx=4,
            ipady=3
        )

        self.label(
            coordinates,
            "Y:",
            12,
            bg=self.panel
        ).pack(
            side="left",
            padx=5
        )

        self.y_entry = self.entry(
            coordinates,
            5
        )

        self.y_entry.pack(
            side="left",
            padx=4,
            ipady=3
        )

        button = self.button(
            self.control_frame,
            "Перемістити",
            self.move_by_coordinates,
            "#1D4ED8",
            20
        )

        button.configure(pady=5)

        button.pack(pady=4)

        self.label(
            self.control_frame,
            f"X: 0–{self.game.width - 1}    "
            f"Y: 0–{self.game.height - 1}",
            10,
            self.muted,
            bg=self.panel
        ).pack(pady=3)

        self.root.bind(
            "<Return>",
            lambda event:
                self.move_by_coordinates()
        )

        self.x_entry.focus_set()

    def create_legend(self, parent):

        container = tk.Frame(
            parent,
            bg=self.panel
        )

        container.pack(
            fill="x",
            padx=10,
            pady=(8, 12)
        )

        self.label(
            container,
            "ПОЗНАЧЕННЯ",
            12,
            self.cyan,
            True,
            self.panel
        ).pack(pady=(0, 10))

        legend = tk.Frame(
            container,
            bg=self.panel
        )

        legend.pack(anchor="center")

        items = [
            ("#38BDF8", "Корабель"),
            ("#22C55E", "Планета"),
            ("#14532D", "Атмосфера"),
            ("#EF4444", "Перешкода"),
            ("#E879F9", "Астероїд"),
            ("#A16207", "Небезпека"),
            ("#164E63", "Дальність"),
            ("#FF0000", "Зіткнення")
        ]

        for index, (color, text) in enumerate(items):

            item = tk.Frame(
                legend,
                bg=self.panel
            )

            item.grid(
                row=index // 2,
                column=index % 2,
                sticky="w",
                padx=12,
                pady=5
            )

            marker = tk.Frame(
                item,
                bg=color,
                width=12,
                height=12
            )

            marker.pack(
                side="left",
                padx=(0, 7)
            )

            tk.Label(
                item,
                text=text,
                bg=self.panel,
                fg=self.text,
                font=("Segoe UI", 10)
            ).pack(side="left")

    def update_stats(self):

        game = self.game

        distance = (
            str(game.max_move)
            if game.max_move is not None
            else "Необмежена"
        )

        text = (
            f"Режим: {game.mode}\n"
            f"Складність: {game.difficulty}\n"
            f"Поле: {game.width} × {game.height}\n"
            f"Планета: {game.planet.size} × "
            f"{game.planet.size}\n"
            f"Корабель: ({game.ship.x}, {game.ship.y})\n"
            f"Виконано ходів: {game.steps}\n"
            f"Перешкод: {game.count}\n"
            f"Нерухомих: {game.count - game.moving}"
            f"    Рухомих: {game.moving}\n"
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
                f"\nШвидкість астероїдів: {speed}"
                f"\nТраєкторія: {travel_min}–{travel_max}"
                f"\nДіагональний рух: {diagonal}"
            )

        self.stats_label.configure(
            text=text
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

        canvas_width = canvas.winfo_width()

        canvas_height = canvas.winfo_height()

        if canvas_width < 50 or canvas_height < 50:

            return

        canvas.delete("all")

        self.cell_size = max(
            8,
            int(
                self.base_cell_size * self.zoom
            )
        )

        field_width = (
            game.width * self.cell_size
        )

        field_height = (
            game.height * self.cell_size
        )

        total_width = max(
            canvas_width,
            field_width + 70
        )

        total_height = max(
            canvas_height,
            field_height + 70
        )

        self.origin_x = (
            total_width - field_width
        ) / 2

        self.origin_y = (
            total_height - field_height
        ) / 2

        canvas.configure(
            scrollregion=(
                0,
                0,
                total_width,
                total_height
            )
        )

        positions = [
            (
                obj,
                obj.at(game.steps)
                if isinstance(
                    obj,
                    MovingObstacle
                )
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
            min(
                13,
                self.cell_size // 2
            )
        )

        for x in range(game.width):

            canvas.create_text(
                self.origin_x
                + x * self.cell_size
                + self.cell_size / 2,

                self.origin_y - 15,

                text=str(x),

                fill=self.muted,

                font=(
                    "Segoe UI",
                    font_size
                )
            )

        for y in range(game.height):

            canvas.create_text(
                self.origin_x - 18,

                self.origin_y
                + y * self.cell_size
                + self.cell_size / 2,

                text=str(y),

                fill=self.muted,

                font=(
                    "Segoe UI",
                    font_size
                )
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

    def get_clicked_cell(self, event):

        canvas_x = self.canvas.canvasx(
            event.x
        )

        canvas_y = self.canvas.canvasy(
            event.y
        )

        x = math.floor(
            (canvas_x - self.origin_x)
            / self.cell_size
        )

        y = math.floor(
            (canvas_y - self.origin_y)
            / self.cell_size
        )

        if not self.game.bounds(x, y):

            return None

        return x, y

    def hover_cell(self, event):

        self.canvas.delete("hover")

        if self.finished:
            return

        if self.control_mode != "mouse":
            return

        cell = self.get_clicked_cell(event)

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
            self.canvas.canvasx(
                self.canvas.winfo_width() - 15
            ),
            self.canvas.canvasy(15),
            text=(
                f"X: {x}   Y: {y}   "
                f"Відстань: {distance:.2f}"
            ),
            anchor="ne",
            fill=color,
            font=("Segoe UI", 11),
            tags="hover"
        )