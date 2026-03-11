import sys
import tkinter as tk
from tkinter import ttk, messagebox, X
from decimal import Decimal, InvalidOperation
import matplotlib
from davcni_sistem import DavcniSistemi as ds

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

        self.rows = []

        self.systems = ds()
        self.systems.splosna_olajsava = 5000
        # self.systems.razredi = ds.slo_brackets

        self.create_layout()
        self.create_plot()
        self.update_plot()
        # self.execute()

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

        # self.firsts_frame = self.tsframe(vcmd)
        # self.second_frame = self.tsframe(vcmd)
        self.firsts_frame = TaxSystem(self.left_master_frame)
        self.second_frame = TaxSystem(self.left_master_frame)
        self.third_frame = TaxSystem(self.left_master_frame)

        self.left_frame_last = ttk.Frame(self.left_master_frame, padding=10)
        self.left_frame_last.pack(side=tk.BOTTOM, fill="y")

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)
        #endregion

        self.prikazi()

        ttk.Button(self.left_frame_last, text="Izvrši", command=self.update_plot).pack(
            fill="x", pady=10
        )

    def tsframe(self, vcmd):

        the_frame = ttk.Frame(self.left_master_frame, padding=10)
        the_frame.pack(side=tk.TOP, fill="y")

        #region ID
        ttk.Label(the_frame, text="ID").pack(anchor="w")
        the_frame.id = ttk.Entry(
            the_frame, validate="key", validatecommand=vcmd
        )
        the_frame.id.pack(fill="x", pady=5)
        the_frame.id.bind("<FocusOut>", self.format_two_decimals)
        #endregion

        #region Allowance
        ttk.Label(the_frame, text="Splošna olajšava (€)").pack(anchor="w")

        the_frame.general_allowance = ttk.Entry(
            the_frame, validate="key", validatecommand=vcmd
        )
        the_frame.general_allowance.pack(fill="x", pady=5)
        the_frame.general_allowance.bind("<FocusOut>", self.format_two_decimals)
        #endregion

        ttk.Separator(the_frame).pack(fill="x", pady=10)

        #region Brackets
        ttk.Label(the_frame, text="Dohodninski razredi").pack(anchor="w")

        table_frame1 = ttk.Frame(the_frame)
        table_frame1.pack(fill="both", expand=True)

        ttk.Label(table_frame1, text="Meja (€)").grid(row=0, column=0)
        ttk.Label(table_frame1, text="Stopnja (%)").grid(row=0, column=1)

        btn_frame1 = ttk.Frame(the_frame)
        btn_frame1.pack(fill="x", pady=10)

        ttk.Button(btn_frame1, text="Dodaj vrstico", command=self.add_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        ttk.Button(btn_frame1, text="Briši zadnjo", command=self.remove_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        #endregion

        return the_frame

    def prikazi(self):

        #prikazi
        grph_frame = ttk.Frame(self.left_frame_last)
        grph_frame.pack(fill="x", pady=10)

        self.prikaz_var = tk.StringVar(self.left_frame_last, value="4")

        values = {"Znesek": "1",
                  "Odstotek": "2",
                  "Delež": "3",
                  "Vse": "4"}

        for (text, value) in values.items():
            tk.Radiobutton(self.left_frame_last, text=text, variable=self.prikaz_var,
                           value=value, indicator=0,
                           background="light blue").pack(side=tk.LEFT)

        self.prikaz_var.set("4")


    # -----------------------
    # TABELA
    # -----------------------
    def add_row(self):
        vcmd = (self.root.register(self.validate_decimal), "%P")

        row_index = len(self.rows) + 1

        entry_limit = ttk.Entry(
            self.table_frame1, validate="key", validatecommand=vcmd
        )
        entry_rate = ttk.Entry(
            self.table_frame1, validate="key", validatecommand=vcmd
        )

        entry_limit.grid(row=row_index, column=0, padx=5, pady=2)
        entry_rate.grid(row=row_index, column=1, padx=5, pady=2)

        entry_limit.bind("<FocusOut>", self.format_two_decimals)
        entry_rate.bind("<FocusOut>", self.format_two_decimals)

        self.rows.append((entry_limit, entry_rate))

    def remove_row(self):
        if self.rows:
            e1, e2 = self.rows.pop()
            e1.destroy()
            e2.destroy()

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

        x_vals_a = []
        y_vals1_a = []

        x_vals, y_vals1 = self.draw_a_system(ds.sistemi[0], "red")
        self.draw_a_system(ds.sistemi[1], "blue")

        # taxsys2 = davcni_sistem.DavcniSistem(5000, ds.hr_brackets)
        # self.draw_a_system(taxsys2, "blue")

        return x_vals, y_vals1

    def draw_a_system(self, ts, color):

        x_vals, y_vals1, y_vals2, y_vals3 = ts.get_taxes()
        # izbira = self.prikaz_var.get()
        izbira = "4"

        if izbira == "1" or izbira == "4":
            self.ax.plot(x_vals, y_vals1, linestyle="dotted", color=color)

        if izbira == "2" or izbira == "4":
            self.ax.plot(x_vals, y_vals2, color=color)

        if izbira == "3" or izbira == "4":
            self.ax.plot(x_vals, y_vals3, linestyle="dashed", color=color)
            self.ax.fill_between(x_vals, y_vals3, 0, alpha=0.2, color=color)

        return x_vals, y_vals1


    # -----------------------
    # IZVRŠI
    # -----------------------


if __name__ == "__main__":
    root = tk.Tk()
    app = DohodninarApp(root)
    root.mainloop()