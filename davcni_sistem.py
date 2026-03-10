import sys
from decimal import Decimal
import numpy as np

class DavcniSistemi:

    max_income = 0
    max_limit = 0

    sistemi = []

    def __init__(self):
        pass

    def add_system(self, system):
        self.sistemi.append(system)
        self.max_income = max(self.max_income, system.razredi[-2][0] * 1.2)

    slo_brackets = [
        (9721.43, 0.16),
        (28592.44, 0.26),
        (57184.88, 0.33),
        (82346.23, 0.39),
        (sys.float_info.max, 0.50),
    ]

    hr_brackets = [
        (50000, 0.20),
        (sys.float_info.max, 0.30)
    ]



class DavcniSistem:

    def __init__(self, splosna_olajsava=0.0, razredi=None, stepsn=200):
        self._splosna_olajsava = splosna_olajsava
        self._razredi = []
        self.nofsteps = 200

        if razredi:
            self.razredi = razredi

    # -------------------------
    # SPLOŠNA OLAJŠAVA
    # -------------------------
    @property
    def splosna_olajsava(self):
        return self._splosna_olajsava

    @splosna_olajsava.setter
    def splosna_olajsava(self, value):
        self._splosna_olajsava = value

    # -------------------------
    # DAVČNI RAZREDI
    # -------------------------
    @property
    def razredi(self):
        return self._razredi

    @razredi.setter
    def razredi(self, razredi):
        self._razredi = [
            (meja, stopnja)
            for meja, stopnja in razredi
        ]

    # -------------------------
    # DODAJ RAZRED
    # -------------------------
    def dodaj_razred(self, meja, stopnja):
        self._razredi.append(
            (meja, stopnja)
        )

    def get_taxes(self):
        return self.calculate_tax_values(self.splosna_olajsava, self.razredi)

    def calculate_tax_values(self, allowance, brackets):
        max_income = brackets[-2][0] * 1.2

        x_vals = []
        y_vals1 = []
        y_vals2 = []
        y_vals3 = []

        x_vals = [float(income) for income in range(0, int(max_income) + 1, int(max_income / self.nofsteps))]

        y_vals1 = [float(self.calculate_tax_in_cash(income, allowance, brackets)) for income in x_vals]

        y_vals2 = np.divide(y_vals1, x_vals)
        y_vals2 = [y2 * max(y_vals1) for y2 in y_vals2]

        y_vals3 = [float(self.calculate_tax_in_share(income, allowance, brackets) * max(y_vals1)) for income in x_vals]

        return x_vals, y_vals1, y_vals2, y_vals3

    def calculate_tax_in_cash(self, income, allowance, brackets):
        taxable = max(0, float(income) - float(allowance))
        tax = 0
        previous_limit = 0

        for limit, rate in brackets:
            if taxable > limit:
                tax += (limit - previous_limit) * rate
                previous_limit = limit
            else:
                tax += (taxable - previous_limit) * rate
                return tax

        return tax

    def calculate_tax_in_share(self, income, allowance, brackets):
        taxable = max(0, float(income) - float(allowance))
        tax = 0
        previous_limit = 0

        for limit, rate in brackets:
            if income <= allowance:
                return 0
            elif taxable > limit:
                previous_limit = limit
            else:
                tax = rate
                return tax

        # če presega zadnji razred
        if taxable > previous_limit:
            tax = rate

        return tax
