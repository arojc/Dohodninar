import tkinter as tk
from tkinter import ttk, messagebox, X
from decimal import Decimal, InvalidOperation
import matplotlib

import tax_calculator

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tax_calculator import slo_brackets, calculate_tax_values


class DohodninarApp:

    def __init__(self, root):
        self.prikaz_var = None
        self.root = root
        self.root.title("Dohodninar")
        self.root.geometry("1100x650")

        self.rows = []

        self.create_layout()
        self.create_plot()
        self.vnesi_slo_razrede()
        self.execute()

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
        self.left_frame = ttk.Frame(self.root, padding=10)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        vcmd = (self.root.register(self.validate_decimal), "%P")

        ttk.Label(self.left_frame, text="Splošna olajšava (€)").pack(anchor="w")

        self.general_allowance = ttk.Entry(
            self.left_frame, validate="key", validatecommand=vcmd
        )
        self.general_allowance.pack(fill="x", pady=5)
        self.general_allowance.bind("<FocusOut>", self.format_two_decimals)

        ttk.Separator(self.left_frame).pack(fill="x", pady=10)

        ttk.Label(self.left_frame, text="Dohodninski razredi").pack(anchor="w")

        self.table_frame = ttk.Frame(self.left_frame)
        self.table_frame.pack(fill="both", expand=True)

        ttk.Label(self.table_frame, text="Meja (€)").grid(row=0, column=0)
        ttk.Label(self.table_frame, text="Stopnja (%)").grid(row=0, column=1)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Dodaj vrstico", command=self.add_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        ttk.Button(btn_frame, text="Briši zadnjo", command=self.remove_row).pack(
            side="left", expand=True, fill="x", padx=2
        )

        self.prikazi()

        ttk.Button(self.left_frame, text="Izvrši", command=self.execute).pack(
            fill="x", pady=10
        )

    def prikazi(self):

        #prikazi
        grph_frame = ttk.Frame(self.left_frame)
        grph_frame.pack(fill="x", pady=10)

        self.prikaz_var = tk.StringVar(self.left_frame, value="4")

        values = {"Znesek": "1",
                  "Odstotek": "2",
                  "Delež": "3",
                  "Vse": "4"}

        for (text, value) in values.items():
            tk.Radiobutton(self.left_frame, text=text, variable=self.prikaz_var,
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
            self.table_frame, validate="key", validatecommand=vcmd
        )
        entry_rate = ttk.Entry(
            self.table_frame, validate="key", validatecommand=vcmd
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

    def new_brackets(self):
        new_brackets = []

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

    def update_plot(self, brackets, allowance):
        self.ax.clear()

        x_vals, y_vals = self.draw_share_rate(brackets, allowance)

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

    def draw_share_rate(self, brackets, allowance):
        # self.ax.clear()

        if not brackets:
            return

        x_vals, y_vals, x_vals1, y_vals1, x_vals2, y_vals2 = calculate_tax_values(allowance, brackets)
        izbira = self.prikaz_var.get()

        # Izris
        if izbira == "1" or izbira == "4":
            self.ax.plot(x_vals, y_vals)
        if izbira == "2" or izbira == "4":
            self.ax.plot(x_vals1, y_vals1)
            self.ax.fill_between(x_vals1, y_vals1, 0, alpha=0.3)
        if izbira == "3" or izbira == "4":
            self.ax.plot(x_vals2, y_vals2)

        # self.ax.plot(x_vals1, y_vals1)
        # self.ax.fill_between(x_vals1, y_vals1, 0, alpha=0.3)
        # self.ax.plot(x_vals, y_vals)
        # self.ax.plot(x_vals2, y_vals2)

        return x_vals, y_vals

    def first_ax(self):

        self.ax.set_title("Progresivna dohodnina")
        self.ax.set_xlabel("Bruto dohodek (€)")
        self.ax.set_ylabel("Dohodnina (€)")

    def plot_effective_rate(self):
        if not self.x_vals or not self.y_vals:
            return

        # izračun efektivne stopnje
        rates = []
        for x, y in zip(self.x_vals, self.y_vals):
            if x > 0:
                rates.append((y / x) * 100)
            else:
                rates.append(0)

        # če desna os še ne obstaja, jo ustvari
        if not hasattr(self, "ax2"):
            return

        # nariši krivuljo na desni osi
        self.ax2.plot(self.x_vals, rates)

        self.canvas.draw()

    # -----------------------
    # IZVRŠI
    # -----------------------
    def execute(self):
        try:
            allowance = Decimal(self.general_allowance.get() or "0")

            brackets = []
            for e_limit, e_rate in self.rows:
                if e_limit.get() and e_rate.get():
                    limit = Decimal(e_limit.get())
                    rate = Decimal(e_rate.get()) / 100
                    brackets.append((limit, rate))

            brackets.sort(key=lambda x: x[0])

            if not brackets:
                messagebox.showerror("Napaka", "Vnesi vsaj en razred.")
                return

            self.update_plot(brackets, allowance)

        except Exception as e:
            messagebox.showerror("Napaka", str(e))

    def vnesi_slo_razrede(self):
        # Vnese slovenske dohodninske razrede (letna lestvica)
        # in nastavi splošno olajšavo.

        # Splošna olajšava (osnovna)
        splosna_olajsava = "5000.00"

        # # ---- Počisti obstoječe vrstice ----
        # while self.rows:
        #     self.remove_row()

        # ---- Nastavi splošno olajšavo ----
        self.general_allowance.delete(0, tk.END)
        self.general_allowance.insert(0, splosna_olajsava)

        # ---- Vnesi nove razrede ----
        for meja, stopnja in slo_brackets:
            self.add_row()
            entry_limit, entry_rate = self.rows[-1]

            entry_limit.insert(0, meja)
            entry_rate.insert(0, stopnja)


if __name__ == "__main__":
    root = tk.Tk()
    app = DohodninarApp(root)
    root.mainloop()