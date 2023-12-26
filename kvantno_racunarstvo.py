"""Biblioteke"""

import sqlite3
from qiskit import QuantumCircuit, Aer, execute
import string
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

"""1. Emitent"""

class Emitent:
    def __init__(self, db_file='novcanice.db'):
        self.simulator = Aer.get_backend('qasm_simulator')
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self._kreiraj_bazu()

    def _kreiraj_bazu(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE novcanice
                              (serijski_broj TEXT PRIMARY KEY,
                               kvantno_stanje TEXT,
                               status TEXT)''')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def generisi_serijski_broj1(self):
        return ''.join(random.choices(string.digits, k=4))

    def generisi_serijski_broj(self):
        serijski_broj = ''

        simulator = Aer.get_backend('qasm_simulator')

        for _ in range(4):  # Generisanje svake cifre serijskog broja
            qc = QuantumCircuit(1, 1)
            qc.h(0)  # Hadamardova kapija za stvaranje superpozicije
            qc.measure(0, 0)

            rezultat = execute(qc, simulator, shots=1).result()
            merenja = rezultat.get_counts(qc)
            cifra = '0' if '0' in merenja else '1'  # Odabir cifre na osnovu merenja

            random_mnozilac = random.randint(1, 9)  # Slučajni množilac od 1 do 9
            krajnja_cifra = str((int(cifra) * random_mnozilac) % 10)
            serijski_broj += krajnja_cifra

        return serijski_broj

    def generisi_kvantno_stanje(self):
        broj_stanja = random.randint(1, 8)
        stanja = []

        simulator = Aer.get_backend('qasm_simulator')

        for _ in range(broj_stanja):
            stanje = random.choice(['0', '1', '+', '-'])
            qc = QuantumCircuit(1, 1)

            if stanje == '0':
                pass  # Nema potrebe za dodatnim operacijama
            elif stanje == '1':
                qc.x(0) # Dodavanje X kapije za stanje |1>
            elif stanje == '+':
                qc.h(0) # Dodavanje Hadamardove kapije za stanje |+>
            elif stanje == '-':
                qc.x(0) # Dodavanje X kapije za stanje |->
                qc.h(0) # Dodavanje Hadamardove kapije za stanje |->

            # Dodavanje Hadamardove kapije pre merenja za stanja |+> i |->
            if stanje in ['+', '-']:
                qc.h(0)

            # Dodavanje merenja
            qc.measure(0, 0)

            # Izvršavanje kvantnog kola na simulatoru
            rezultat = execute(qc, simulator, shots=1).result()
            merenja = rezultat.get_counts(qc)

            # Dodavanje rezultata merenja u listu stanja
            mereno_stanje = list(merenja.keys())[0]  # Uzima ključ (rezultat merenja) iz merenja
            if stanje in ['+', '-']:
                mereno_stanje = '+' if mereno_stanje == '0' else '-'
            stanja.append('|' + mereno_stanje + '>')

        return stanja

    def izdaj_novcanicu(self, status):
        serijski_broj = self.generisi_serijski_broj()
        kvantno_stanje = self.generisi_kvantno_stanje()
        cursor = self.conn.cursor()
        if status == 0:
            status = 'U banci'
        else:
            status = 'Izdata'
        stanje_string = ', '.join(kvantno_stanje)
        cursor.execute('INSERT INTO novcanice (serijski_broj, kvantno_stanje, status) VALUES (?, ?, ?)',
                       (serijski_broj, stanje_string, status))
        self.conn.commit()
        return serijski_broj, kvantno_stanje

    def verifikuj_novcanicu(self, serijski_broj):
        cursor = self.conn.cursor()
        cursor.execute('SELECT kvantno_stanje, status FROM novcanice WHERE serijski_broj=?', (serijski_broj,))
        result = cursor.fetchone()

        if result:
            sacuvano_stanje, status = result
            if status == 'Izdata' or status == 'U banci':
                return "Postoji novčanica sa unetim serijskim brojem"
            else:
                return "Ne postoji novčanica sa unetim serijskim brojem"

    def __del__(self):
        self.conn.close()

"""2. Korisnik"""

class Korisnik:
    def __init__(self, emitent, db_file='novcanik.db'):
        self.emitent = emitent
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.kreiraj_bazu()

    def kreiraj_bazu(self):
        cursor = self.conn.cursor()
        # Kreiranje tabele, ako ne postoji
        cursor.execute('''CREATE TABLE IF NOT EXISTS novcanik
                          (serijski_broj TEXT PRIMARY KEY,
                           kvantno_stanje TEXT)''')
        self.conn.commit()

        # Dodavanje kolone kvantno_stanje
        try:
            cursor.execute('ALTER TABLE novcanik ADD COLUMN kvantno_stanje TEXT')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def zahtevaj_novcanicu(self, status):
        serijski_broj, kvantno_stanje = self.emitent.izdaj_novcanicu(status)
        cursor = self.conn.cursor()
        # Enkodiranje originalnih stanja u obliku random brojeva
        enkodirana_stanja = [str(random.randint(0, 1000)) for _ in kvantno_stanje]
        enk_str = ', '.join(enkodirana_stanja)
        # Unos serijskog broja i kvantnog stanja u tabelu
        cursor.execute('INSERT INTO novcanik (serijski_broj, kvantno_stanje) VALUES (?, ?)',
                       (serijski_broj, enk_str))
        self.conn.commit()
        return serijski_broj, kvantno_stanje


    def verifikuj_novcanicu(self, serijski_broj):
        return self.emitent.verifikuj_novcanicu(serijski_broj)

    def __del__(self):
        self.conn.close()

"""3. Falsifikator"""

class Falsifikator:
    def __init__(self, emitent):
        self.emitent = emitent
        
    def pokusaj_falsifikovanja(self, serijski_broj, kvantno_stanje):
        # Simulacija pokušaja falsifikovanja kvantnog stanja
        pogodjeno_stanje = self.emitent.generisi_kvantno_stanje()
        if(pogodjeno_stanje==kvantno_stanje):
            return
        else:
            return False

"""Interfejs Kvantna banka"""


class InterfejsKvantnaBanka:
    def __init__(self, emitent, korisnik, falsifikator):
        self.emitent = emitent
        self.korisnik = korisnik
        self.falsifikator = falsifikator

        self.root = tk.Tk()
        self.root.title("Kvantno Bankarstvo")
        self.root.geometry("300x700")
        self.root.protocol("WM_DELETE_WINDOW", self.zatvori_prozor)

        # Povećane dimenzije dugmadi
        button_width = 20
        button_height = 3

        tk.Label(self.root, text="").pack()
        tk.Label(self.root, text="Za Emitente").pack()
        tk.Label(self.root, text="").pack()
        tk.Button(self.root, text="Izdaj Novčanicu", width=button_width, height=button_height,
                  command=self.izdaj_novcanicu).pack()
        tk.Button(self.root, text="Pregled Novčanica", width=button_width, height=button_height,
                  command=self.pregled_novcanica).pack()
        tk.Button(self.root, text="Verifikuj Novčanicu", width=button_width, height=button_height,
                  command=self.verifikuj_novcanicu).pack()
        tk.Button(self.root, text="Obriši Sve Novčanice", width=button_width, height=button_height,
                  command=self.obrisi_sve_novcanice).pack()

        tk.Label(self.root, text="").pack()
        tk.Label(self.root, text="Za Korisnika").pack()
        tk.Label(self.root, text="").pack()
        tk.Button(self.root, text="Zahtevaj Novčanicu", width=button_width, height=button_height,
                  command=self.zahtevaj_novcanicu).pack()
        tk.Button(self.root, text="Pregled Novčanika", width=button_width, height=button_height,
                  command=self.pregled_novcanika).pack()
        tk.Button(self.root, text="Obriši Ceo Novčanik", width=button_width, height=button_height,
                    command=self.obrisi_ceo_novcanik).pack()

        tk.Label(self.root, text="").pack()
        tk.Label(self.root, text="Za Falsifikatora").pack()
        tk.Label(self.root, text="").pack()
        tk.Button(self.root, text="Pokušaj Falsifikovanja", width=button_width, height=button_height,
                  command=self.pokusaj_falsifikovanja).pack()

    def izdaj_novcanicu(self):
        status = 0
        serijski_broj, kvantno_stanje = self.emitent.izdaj_novcanicu(status)
        messagebox.showinfo("Izdavanje Novčanice", f"Serijski broj: {serijski_broj}, Kvantno stanje: {kvantno_stanje}")

    def proveri_postojanje_novcanice(self, serijski_broj):
        cursor = self.emitent.conn.cursor()
        cursor.execute('SELECT serijski_broj FROM novcanice WHERE serijski_broj=?', (serijski_broj,))
        result = cursor.fetchone()
        return result is not None

    def verifikuj_novcanicu(self):
        # Unos serijskog broja za verifikaciju
        serijski_broj = simpledialog.askstring("Verifikacija Novčanice", "Unesite serijski broj:")

        # Provera da li postoji novčanica sa unetim serijskim brojem
        if not self.proveri_postojanje_novcanice(serijski_broj):
            messagebox.showinfo("Verifikacija Novčanice", "Novčanica sa unetim serijskim brojem ne postoji.")
            return


        # Verifikacija novčanice i prikaz rezultata
        rezultat = self.korisnik.verifikuj_novcanicu(serijski_broj)
        messagebox.showinfo("Status i Stanje", f"{rezultat}\nNovčanica je validna.")

    def pokusaj_falsifikovanja(self):
        # Unos serijskog broja za pokušaj falsifikovanja
        serijski_broj = simpledialog.askstring("Falsifikovanje Novčanice", "Unesite serijski broj za falsifikovanje:")

        # Provera da li postoji novčanica sa unetim serijskim brojem
        if not self.proveri_postojanje_novcanice(serijski_broj):
            messagebox.showinfo("Rezultat Falsifikovanja", "Novčanica sa unetim serijskim brojem ne postoji.")
            return

        cursor = self.emitent.conn.cursor()
        cursor.execute('SELECT kvantno_stanje FROM novcanice WHERE serijski_broj=?', (serijski_broj,))
        kvantno_stanje = cursor.fetchone()
        uspeh = self.falsifikator.pokusaj_falsifikovanja(serijski_broj, kvantno_stanje)

        if uspeh:
            poruka = "Falsifikacija uspešna."
        else:
            poruka = "Falsifikacija neuspešna."
        messagebox.showinfo("Rezultat Falsifikovanja", poruka)

    def pregled_novcanica(self):
        cursor = self.emitent.conn.cursor()
        cursor.execute('SELECT serijski_broj, kvantno_stanje, status FROM novcanice')
        novcanice = cursor.fetchall()
        poruka = "\n".join(
            [f"Serijski broj: {serijski}, Stanje: {stanje}, Status: {status}" for serijski, stanje, status in
             novcanice])
        messagebox.showinfo("Pregled Novčanica", poruka)

    def pregled_novcanika(self):
        cursor = self.korisnik.conn.cursor()
        cursor.execute('SELECT serijski_broj, kvantno_stanje FROM novcanik')
        novcanik = cursor.fetchall()
        poruka = "\n".join(
            [f"Serijski broj: {serijski}, Stanje: {stanje}" for serijski, stanje in
             novcanik])
        messagebox.showinfo("Pregled Novčanika", poruka)

    def obrisi_sve_novcanice(self):
        # Provera da li je baza podataka 'novcanice' prazna
        cursor = self.emitent.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM novcanice')
        broj_redova = cursor.fetchone()[0]

        if broj_redova == 0:
            messagebox.showinfo("Brisanje Svega", "Baza podataka 'novcanice' je već prazna.")
        else:
            odgovor = messagebox.askyesno("Brisanje Svega",
                                          "Da li ste sigurni da želite obrisati sve novčanice iz Kvantne banke?")
            if odgovor:
                cursor.execute('DELETE FROM novcanice')
                self.emitent.conn.commit()
                cursor2 = self.korisnik.conn.cursor()
                cursor2.execute('DELETE FROM novcanik')
                self.korisnik.conn.commit()
                messagebox.showinfo("Brisanje Svega", "Sve novčanice su obrisane iz Kvantne banke.")

    def obrisi_ceo_novcanik(self):
        # Provera da li je baza podataka 'novcanik' prazna
        cursor = self.korisnik.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM novcanik')
        broj_redova = cursor.fetchone()[0]

        if broj_redova == 0:
            messagebox.showinfo("Brisanje Svega iz Novčanika", "Baza podataka 'novcanik' je već prazna.")
        else:
            odgovor = messagebox.askyesno("Brisanje Svega",
                                          "Da li ste sigurni da želite obrisati sve novčanice iz novčanika?")
            if odgovor:
                cursor.execute('DELETE FROM novcanik')
                self.korisnik.conn.commit()
                cursor2 = self.emitent.conn.cursor()
                cursor2.execute('UPDATE novcanice SET status="U banci"')
                self.emitent.conn.commit()
                messagebox.showinfo("Brisanje Svega iz Novčanika", "Sve novčanice su obrisane iz novčanika.")

    def zahtevaj_novcanicu(self):
        status = 1
        serijski_broj, kvantno_stanje = self.korisnik.zahtevaj_novcanicu(status)
        messagebox.showinfo("Dobijena Novčanica", f"Serijski broj: {serijski_broj}")

    def zatvori_prozor(self):
        odgovor = messagebox.askyesno("Zatvaranje Prozora", "Da li ste sigurni da želite zatvoriti prozor?")
        if odgovor:
            self.root.destroy()

    def pokreni(self):
        self.root.mainloop()


"""Pokretanje sistema"""
def main():
    # Definicija baze podataka
    db_file = 'novcanice.db'
    db_file2 = 'novcanik.db'

    # Kreiranje jednog emitenta
    emitent = Emitent(db_file=db_file)

    # Kreiranje jednog korisnika povezanog sa emitentom
    korisnik = Korisnik(emitent, db_file=db_file2)

    # Kreiranje falsifikatora povezanog sa emitentom
    falsifikator = Falsifikator(emitent)

    # Kreiranje i pokretanje interfejsa
    interfejs = InterfejsKvantnaBanka(emitent, korisnik, falsifikator)
    interfejs.pokreni()

if __name__ == '__main__':
    main()
