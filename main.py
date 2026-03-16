import sys
import tkinter as tk
from tkinter import ttk, messagebox, X
from decimal import Decimal, InvalidOperation
from tkinter.constants import *
import matplotlib

from davcni_sistem import DavcniSistemi

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui import TaxSystem


class DohodninarApp:

    def __init__(self, root):
        self.prikaz_var = None
        self.root = root
        self.root.title("Dohodninar")
        self.root.geometry("1100x650")

        self.sys_frames = []

        self.systems = DavcniSistemi()

        self.create_layout()
        self.create_plot()
        self.update_plot()

    # -----------------------
    # VALIDACIJA
    # -----------------------
    def validate_decimal(self, value):
        if value == "":
            return True
        try:
            d = Decimal(value)
        except InvalidOperation:
            return False

        if d < 0:
            return False

        if d.as_tuple().exponent < -2:
            return False

        return True

    def format_two_decimals(self, event):
        widget = event.widget
        value = widget.get()
        if value != "":
            try:
                d = Decimal(value)
                widget.delete(0, tk.END)
                widget.insert(0, f"{d:.2f}")
            except:
                pass

    # -----------------------
    # LAYOUT
    # -----------------------
    def create_layout(self):

        vcmd = (self.root.register(self.validate_decimal), "%P")

        #region Frames
        self.left_master_frame = ttk.Frame(self.root, padding=10)
        self.left_master_frame.pack(side="left", fill="y")

        self.left_scrolling_frame = ttk.Frame(self.left_master_frame, padding=10)

        self.left_fixed_frame = ttk.Frame(self.left_master_frame, padding=10)

        self.left_master_frame.rowconfigure(0, weight=1)  # zgornji zavzame preostali prostor

        self.left_scrolling_frame.grid(row=0, column=0, sticky="nsew")
        self.left_fixed_frame.grid(row=1, column=0, sticky="ew")

        self.create_scrolling()

        for s in self.systems.sistemi:
            self.sys_frames.append(TaxSystem(self.left_subframe, s))

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)
        #endregion

        self.prikazi()

        # ttk.Separator(self.left_fixed_frame).pack(fill="x", pady=10)
        #
        # ttk.Button(self.left_fixed_frame, text="Izvrši", command=self.update_plot).pack(
        #     fill="x", pady=10
        # )

    def create_scrolling(self):
        canvas = tk.Canvas(self.left_scrolling_frame)
        scrollbar = ttk.Scrollbar(self.left_scrolling_frame, orient="vertical", command=canvas.yview)

        self.left_subframe = ttk.Frame(canvas)

        self.left_subframe.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.left_subframe, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def prikazi(self):

        ttk.Separator(self.left_fixed_frame).pack(fill="x", pady=10)

        ttk.Button(self.left_fixed_frame, text="Izvrši", command=self.update_plot).pack(
            fill="x", pady=10, side=tk.RIGHT
        )

        #prikazi

        self.prikaz_var = tk.StringVar(self.left_fixed_frame, value="4")

        values = {"Znesek": "1",
                  "Odstotek": "2",
                  "Delež": "3",
                  "Vse": "4"}

        for (text, value) in values.items():
            tk.Radiobutton(self.left_fixed_frame, text=text, variable=self.prikaz_var,
                           value=value, indicator=0,
                           background="light blue").pack(side=tk.LEFT)

        self.prikaz_var.set("4")


    # -----------------------
    # GRAF
    # -----------------------
    def create_plot(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Premakni osi na ničlo
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['bottom'].set_position('zero')

        # Enaka skala na obeh oseh
        self.ax.set_aspect('equal', adjustable='box')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_plot(self):

        for f in self.sys_frames:
            f.data_to_system()

        self.ax.clear()

        x_vals, y_vals = self.draw_share_rate()

        # ---- Fiksna spodnja meja 0 ----
        max_tax = max(y_vals) if y_vals else 1
        self.ax.set_ylim(bottom=0)
        self.ax.set_xlim(left=0)

        # ---- DESNA OS kot sekundarna skala ----
        if hasattr(self, "ax2"):
            self.ax2.remove()

        self.ax2 = self.ax.secondary_yaxis(
            'right',
            functions=(
                lambda y: (y / max_tax) * 100,
                lambda p: (p / 100) * max_tax
            )
        )

        self.ax2.set_ylabel("Obremenitev (%)")
        self.ax2.set_yticklabels([f"{i * 10}%" for i in range(11)])
        self.ax2.set_yticks(range(0, 101, 10))

        self.x_vals = x_vals
        self.y_vals = y_vals

        self.canvas.draw()

    def draw_share_rate(self):
        self.ax.clear()

        graph_data = self.systems.get_graph_data()

        x_vals, y_vals1 = self.draw_a_system(graph_data[0], "red")
        self.draw_a_system(graph_data[1], "green")
        self.draw_a_system(graph_data[2], "blue")

        return x_vals, y_vals1

    def draw_a_system(self, ts, color):
        izbira = self.prikaz_var.get()

        if izbira == "1" or izbira == "4":
            self.ax.plot(ts[0], ts[1], linestyle="dotted", color=color)

        if izbira == "2" or izbira == "4":
            self.ax.plot(ts[0], ts[2], color=color)

        if izbira == "3" or izbira == "4":
            self.ax.plot(ts[0], ts[3], linestyle="dashed", color=color)
            self.ax.fill_between(ts[0], ts[3], 0, alpha=0.2, color=color)

        return ts[0], ts[1]


    # -----------------------
    # IZVRŠI
    # -----------------------


if __name__ == "__main__":
    root = tk.Tk()
    app = DohodninarApp(root)
    root.mainloop()