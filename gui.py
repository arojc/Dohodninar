import tkinter as tk
from tkinter import ttk


class TaxSystem():

    def __init__(self, parent):

        self.the_frame = ttk.Frame(parent, padding=10)
        self.the_frame.pack(side=tk.TOP, fill="y")

        #region ID
        ttk.Label(self.the_frame, text="ID").pack(anchor="w")
        self.id = ttk.Entry(self.the_frame, validate="key")
        self.id.pack(fill="x", pady=5)
        self.id.insert(0, "GGG")
        # the_frame.id.bind("<FocusOut>", self.format_two_decimals)
        #endregion

        #region Allowance
        ttk.Label(self.the_frame, text="Splošna olajšava (€)").pack(anchor="w")

        self.general_allowance = ttk.Entry(self.the_frame)
        self.general_allowance.pack(fill="x", pady=5)
        # the_frame.general_allowance.bind("<FocusOut>", self.format_two_decimals)
        #endregion

        ttk.Separator(self.the_frame).pack(fill="x", pady=10)

        #region Brackets
        ttk.Label(self.the_frame, text="Dohodninski razredi").pack(anchor="w")

        self.table_frame1 = ttk.Frame(self.the_frame)
        self.table_frame1.pack(fill="both", expand=True)

        ttk.Label(self.table_frame1, text="Meja (€)").grid(row=0, column=0)
        ttk.Label(self.table_frame1, text="Stopnja (%)").grid(row=0, column=1)

        self.btn_frame1 = ttk.Frame(self.the_frame)
        self.btn_frame1.pack(fill="x", pady=10)

        ttk.Button(self.btn_frame1, text="Dodaj vrstico", command=self.add_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        ttk.Button(self.btn_frame1, text="Briši zadnjo", command=self.remove_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        #endregion

    # ------------------------
    # Dodaj vrstico
    # ------------------------
    def add_row(self):
        row_index = self.table_row_start + len(self.rows)

        meja = ttk.Entry(self)
        stopnja = ttk.Entry(self)

        meja.grid(row=row_index, column=0, padx=5, pady=2, sticky="ew")
        stopnja.grid(row=row_index, column=1, padx=5, pady=2, sticky="ew")

        self.rows.append((meja, stopnja))

    # ------------------------
    # Odstrani vrstico
    # ------------------------
    def remove_row(self):
        if self.rows:
            meja, stopnja = self.rows.pop()
            meja.destroy()
            stopnja.destroy()

    def draw_from_system(self, system):
        self.id.insert(system.id)
        self.general_allowance.insert(system._splosna_olajsava)
        pass