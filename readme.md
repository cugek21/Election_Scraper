## 🗳️ Czech Election Scraper

A Python script that scrapes election data from [volby.cz](https://www.volby.cz) and exports it to a CSV file.

---

### 📦 Features

* Scrapes official municipal-level election data from the Czech electoral website.
* Extracts:

  * Municipality codes and names
  * Registered voters
  * Issued envelopes
  * Valid votes
  * Votes per party
* Exports results into a structured CSV file.

---

### 🛠 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

**Required packages:**

* `requests`
* `beautifulsoup4`

---

### 🚀 Usage

```bash
python main.py '<URL>' output.csv
```

**Example:**

```bash
python main.py 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xobec=0&xvyber=6203' vysledky.csv
```

---

### 📂 Output Format

The resulting `CSV` file contains:

| Kód | Obec | Voliči v seznamu | Vydané obálky | Platné hlasy | Strana A | Strana B | atd. |
| --- | ---- | ---------------- | ------------- | ------------ | -------- | -------- | ---- |


---

### ⚠️ Notes

* Only works with official election URLs from `volby.cz`.
* If the structure of the source site changes, selectors may need to be updated.

---

### 📄 License

MIT License

Created by Radek Jíša
