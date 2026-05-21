
import sqlite3
import questionary

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# tabela kont bankowych
cursor.execute("""
  CREATE TABLE accounts(
  account_id TEXT PRIMARY KEY,
  owner_name TEXT,
  balance REAL
  )
  """)

# tabela transakcji
cursor.execute("""
  CREATE TABLE transaction_history(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_id TEXT,
  receiver_id TEXT,
  amount REAL,
  status TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  )
""")

klienci = [
    ("ACC01", "Jan Kowalski", 1000.00),
    ("ACC02", "Anna Nowak", 1500.00),
    ("ACC03", "Piotr Michalski", 0.00)
]

cursor.executemany("INSERT INTO accounts VALUES (?, ?, ?)", klienci)

conn.commit()

print("Zainicjowano baze danych pomyslnie!")

def wykonaj_przelew(sender, receiver, amount):
  if (amount<=0):
    print("Nieprawidłowy kwota przelewu!")
    return

  if (sender == receiver):
    print("Nie można wykonać przelewu do samego siebie!")
    return

  cursor.execute("SELECT balance FROM accounts WHERE account_id = ?", (sender,))
  sender_balance = cursor.fetchone()
  if (sender_balance is None):
    print("Brak konta nadawcy!")
    return
  sender_balance = sender_balance[0]

  cursor.execute("SELECT balance FROM accounts WHERE account_id = ?", (receiver,))
  receiver_balance = cursor.fetchone()
  if (receiver_balance is None):
    print("Brak konta odbiorcy!")
    return
  receiver_balance = receiver_balance[0]


  if (amount > sender_balance):
    print("Brak środków na koncie!")
    cursor.execute("INSERT INTO transaction_history (sender_id, receiver_id, amount, status) VALUES (?, ?, ?, ?)", (sender, receiver, amount, "REJECTED"))
    conn.commit()
    return



  try:
    cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_id = ?", (amount, sender))
    # raise Exception("Awaria zasilania serwera bankowego!")
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, receiver))
    cursor.execute("INSERT INTO transaction_history (sender_id, receiver_id, amount, status) VALUES (?, ?, ?, ?)", (sender, receiver, amount, "SUCCESS"))
    conn.commit()
    print("Przelew wykonany pomyslnie!")
  except Exception as e:
    conn.rollback()
    cursor.execute("INSERT INTO transaction_history (sender_id, receiver_id, amount, status) VALUES (?, ?, ?, ?)", (sender, receiver, amount, "FAILED"))
    conn.commit()
    print("Wystąpił błąd podczas wykonania przelewu!")
    print(e)


def kontaInfo():
  cursor.execute("SELECT * FROM accounts")
  uzytk = cursor.fetchall()
  for konto in uzytk:
        print(f"""
          ID konta: {konto[0]}
          Właściciel: {konto[1]}
          Saldo: {konto[2]} PLN
        """)
def transakcjeInfo():
  cursor.execute("SELECT * FROM transaction_history")
  transakcje = cursor.fetchall()
  for t in transakcje:
    print(f"""
      ID transakcji: {t[0]}
      Nadawca: {t[1]}
      Odbiorca: {t[2]}
      Kwota: {t[3]} PLN
      Status: {t[4]}
      Data: {t[5]}
    """)

def wykonajPrzelew():
  cursor.execute("SELECT account_id FROM accounts")
  konta = [konto[0] for konto in cursor.fetchall()]
  cursor.fetchall()
  nadawca = questionary.select(
        "Wybierz nadawce przelewu:",
        choices=konta
    ).ask()
  odbiorca = questionary.select(
        "Wybierz odbiorce przelewu:",
        choices=konta
    ).ask()
  tekst = input("Wprowadz kwote przelewu:")
  try:
    kwota = float(tekst)
    wykonaj_przelew(nadawca, odbiorca, kwota)
  except ValueError:
    print("Nieprawidlowa kwota")



while True:

    wybor = questionary.select(
        "Wybierz opcję z menu:",
        choices=[
            "Wyswietl informacje o kontach uzytkownikow",
            "Wyswietl informacje o transakcjach uzytkownikow",
            "Wykonaj przelew",
            "Koniec programu"
        ]
    ).ask()

    if wybor == "Wyswietl informacje o kontach uzytkownikow":
        kontaInfo()

    elif wybor == "Wyswietl informacje o transakcjach uzytkownikow":
        transakcjeInfo()

    elif wybor == "Wykonaj przelew":
        wykonajPrzelew()

    elif wybor == "Koniec programu":
        print("\nZamykanie programu...")
        break

