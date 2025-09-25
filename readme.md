# 🗳️ Czech Election Scraper

This Python project scrapes official Czech election data from [volby.cz](https://www.volby.cz) and exports results to a CSV file. It is modular and maintainable.

## 📦 Features

- Scrapes official municipal-level election data from the Czech electoral website
- Extracts:
  - Municipality codes and names
  - Registered voters
  - Issued envelopes
  - Valid votes
  - Votes per party
- Exports results into a structured CSV file

## 🛠 Requirements

- Python 3.10
- The following Python packages (see [requirements.txt](requirements.txt)):
  - requests
  - beautifulsoup4

**Install dependencies:**

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python main.py '<URL>' <output.csv>
```

**Example:**

```bash
python3 main.py 'https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=9&xnumnuts=5301' results.csv
```

## 📂 Output Format

The resulting CSV file contains columns:

| Kód | Obec | Voliči v seznamu | Vydané obálky | Platné hlasy | Strana A | Strana B | atd. |
| --- | ---- | ---------------- | ------------- | ------------ | -------- | -------- | ---- |

## 🧩 Project Structure

- `main.py` — Entry point, argument parsing, orchestration
- `scraper_utils.py` — Scraping and extraction helpers
- `csv_utils.py` — CSV writing logic
- `requirements.txt` — Python dependencies
- `results.csv` — Example output

## ⚠️ Notes & Troubleshooting

- Only works with official election URLs from `volby.cz`.
- If the structure of the source site changes, selectors may need to be updated.
- For errors, check your Python version (3.10+) and dependencies.

## 📄 Author

Radek Jíša
