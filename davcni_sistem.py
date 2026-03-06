from decimal import Decimal


class DavcniSistem:

    def __init__(self, splosna_olajsava=0.0, razredi=None):
        self._splosna_olajsava = Decimal(str(splosna_olajsava))
        self._razredi = []

        if razredi:
            self.razredi = razredi

    # -------------------------
    # SPLOŠNA OLAJŠAVA
    # -------------------------
    @property
    def splosna_olajsava(self):
        return float(self._splosna_olajsava)

    @splosna_olajsava.setter
    def splosna_olajsava(self, value):
        self._splosna_olajsava = Decimal(str(value))

    # -------------------------
    # DAVČNI RAZREDI
    # -------------------------
    @property
    def razredi(self):
        return [(float(meja), float(stopnja)) for meja, stopnja in self._razredi]

    @razredi.setter
    def razredi(self, razredi):
        self._razredi = [
            (Decimal(str(meja)), Decimal(str(stopnja)))
            for meja, stopnja in razredi
        ]

    # -------------------------
    # DODAJ RAZRED
    # -------------------------
    def dodaj_razred(self, meja, stopnja):
        self._razredi.append(
            (Decimal(str(meja)), Decimal(str(stopnja)))
        )