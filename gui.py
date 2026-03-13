import tkinter as tk
from tkinter import ttk


class TaxSystem():

    def __init__(self, parent, system):

        self.the_system = system

        self.the_frame = ttk.Frame(parent, padding=10)
        self.the_frame.pack(side=tk.TOP, fill="y")

        #region ID
        ttk.Label(self.the_frame, text="ID").pack(anchor="w")
        self.id = ttk.Entry(self.the_frame, validate="key")
        self.id.pack(fill="x", pady=5)
        #endregion

        #region Allowance
        ttk.Label(self.the_frame, text="Splošna olajšava (€)").pack(anchor="w")

        self.general_allowance = ttk.Entry(self.the_frame)
        self.general_allowance.pack(fill="x", pady=5)
        #endregion

        ttk.Separator(self.the_frame).pack(fill="x", pady=10)

        #region Brackets
        ttk.Label(self.the_frame, text="Dohodninski razredi").pack(anchor="w")

        self.table_frame1 = ttk.Frame(self.the_frame)
        self.table_frame1.pack(fill="both", expand=True)

        ttk.Label(self.table_frame1, text="Meja (€)").grid(row=0, column=0)
        ttk.Label(self.table_frame1, text="Stopnja (%)").grid(row=0, column=1)

        self.brackets = []

        for i, razred in enumerate(system.razredi):
            br1 = ttk.Entry(self.table_frame1, validate="key")
            br1.grid(row=i+1, column=0)
            br2 = ttk.Entry(self.table_frame1, validate="key")
            br2.grid(row=i+1, column=1)
            self.brackets.append((br1, br2))

        self.btn_frame1 = ttk.Frame(self.the_frame)
        self.btn_frame1.pack(fill="x", pady=10)

        ttk.Button(self.btn_frame1, text="Dodaj vrstico", command=self.add_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        ttk.Button(self.btn_frame1, text="Briši zadnjo", command=self.remove_row).pack(
            side="left", expand=True, fill="x", padx=2
        )
        #endregion

        self.fill_data()

    def fill_data(self):
        if self.the_system:
            self.id.insert(0, self.the_system.id)
        else:
            self.id.insert(0, "GGG")
        if self.the_system:
            self.general_allowance.insert(0, self.the_system.splosna_olajsava)
        else:
            self.general_allowance.insert(0, "0")

        for i, razred in enumerate(self.the_system.razredi):
            self.brackets[i][0].insert(0, razred[0])
            self.brackets[i][1].insert(0, razred[1])

    def empty_data(self):
        while len(self.brackets) > 0:
            self.remove_row()

    # ------------------------
    # Dodaj vrstico
    # ------------------------
    def add_row(self):
        row_index = len(self.brackets)

        meja = ttk.Entry(self.table_frame1)
        stopnja = ttk.Entry(self.table_frame1)

        meja.grid(row=row_index, column=0, padx=5, pady=2, sticky="ew")
        stopnja.grid(row=row_index, column=1, padx=5, pady=2, sticky="ew")

        self.brackets.append((meja, stopnja))

    def data_to_system(self):
        self.the_system.id(self.id.get())
        self.the_system.splosna_olajsava(self.try_to_compile(self.general_allowance.get()))

        new_brackets = []
        for row in self.brackets:
            new_brackets.append(row)

        self.the_system.razredi = new_brackets


    def try_to_compile(self, input):
        try:
            return float(input)
        except:
            return 0


    # ------------------------
    # Odstrani vrstico
    # ------------------------
    def remove_row(self):
        if self.brackets:
            meja, stopnja = self.brackets.pop()
            meja.destroy()
            stopnja.destroy()

    def draw_from_system(self, system):
        self.id.insert(system.id)
        self.general_allowance.insert(system._splosna_olajsava)
        pass