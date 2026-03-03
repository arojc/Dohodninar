import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DohodninarApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Dohodninar")
        self.root.geometry("1100x650")

        self.rows = []

        self.create_layout()
        self.create_plot()
        self.slo_razredi()
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

        ttk.Button(self.left_frame, text="Izvrši", command=self.execute).pack(
            fill="x", pady=10
        )

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

    # -----------------------
    # IZRAČUN DAVKA
    # -----------------------
    def calculate_tax(self, income, allowance, brackets):
        taxable = max(0, income - allowance)
        tax = Decimal("0")
        previous_limit = Decimal("0")

        for limit, rate in brackets:
            if taxable > limit:
                tax += (limit - previous_limit) * rate
                previous_limit = limit
            else:
                tax += (taxable - previous_limit) * rate
                return tax

        # če presega zadnji razred
        if taxable > previous_limit:
            tax += (taxable - previous_limit) * brackets[-1][1]

        return tax

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

        if not brackets:
            return

        max_income = float(brackets[-1][0]) * 1.2

        x_vals = []
        y_vals = []

        income = Decimal("0")
        step = max_income / 200

        while income <= max_income:
            tax = self.calculate_tax(income, allowance, brackets)
            x_vals.append(float(income))
            y_vals.append(float(tax))
            income += Decimal(step)

        self.ax.plot(x_vals, y_vals)
        self.ax.set_title("Progresivna dohodnina")
        self.ax.set_xlabel("Bruto dohodek (€)")
        self.ax.set_ylabel("Dohodnina (€)")
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

    def slo_razredi(self):
        """
        Vnese slovenske dohodninske razrede (letna lestvica)
        in nastavi splošno olajšavo.
        """

        # ---- Slovenska dohodninska lestvica ----
        # (meja razreda, stopnja %)
        slo_brackets = [
            ("8500.00", "16.00"),
            ("25000.00", "26.00"),
            ("50000.00", "33.00"),
            ("72000.00", "39.00"),
            ("100000.00", "50.00"),
        ]

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