import logging
from decimal import Decimal, InvalidOperation

# -----------------------
# IZRAČUN DAVKA
# -----------------------
def calculate_tax_values(allowance, brackets):
    max_income = brackets[-1][0] * Decimal(1.2)

    x_vals = []
    y_vals = []
    x_vals1 = []
    y_vals1 = []
    x_vals2 = []
    y_vals2 = []

    income = Decimal("0")
    step = max_income / 200

    while income <= max_income:
        tax = calculate_tax_in_cash(income, allowance, brackets)
        x_vals.append(float(income))
        y_vals.append(float(tax))

        x_vals2.append(float(income))
        if income != Decimal("0"):
            y_vals2.append(float(tax)/float(income))
        else:
            y_vals2.append(0.0)

        income += step

    max_tax = y_vals[-1] if y_vals else Decimal("0")

    y_vals2 = [y * max_tax for y in y_vals2]


    income = Decimal("0")

    while income <= max_income:
        tax = calculate_tax_in_share(income, allowance, brackets)
        x_vals1.append(float(income))
        y_vals1.append(float(tax)*float(max_tax))
        income += step
    income = Decimal("0")


    return x_vals, y_vals, x_vals1, y_vals1, x_vals2, y_vals2

def calculate_tax_in_cash(income, allowance, brackets):
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

def calculate_tax_in_share(income, allowance, brackets):
    taxable = max(0, income - allowance)
    tax = Decimal("0")
    previous_limit = Decimal("0")

    for limit, rate in brackets:
        if income <= allowance:
            return Decimal("0")
        elif taxable > limit:
            # tax += (limit - previous_limit) * rate
            previous_limit = limit
        else:
            tax = rate
            return tax

    # če presega zadnji razred
    if taxable > previous_limit:
        tax = rate

    return tax

def calculate_tax_in_share1(income, allowance, brackets):
    taxable = max(0, income - allowance)
    tax = Decimal("0")
    previous_limit = Decimal("0")

    for limit, rate in brackets:
        if taxable > limit:
            tax = rate * 100000
            previous_limit = limit
        else:
            tax = rate * 100000
            return tax

    # če presega zadnji razred
    if taxable > previous_limit:
        tax  = rate * 100000

    print(f"Taxable: {taxable}, Tax: {tax}%")
    return tax


# ---- Slovenska dohodninska lestvica ----
# (meja razreda, stopnja %)
slo_brackets = [
    ("9721.43", "16.00"),
    ("28592.44", "26.00"),
    ("57184.88", "33.00"),
    ("82346.23", "39.00"),
    ("100000.00", "50.00"),
]

