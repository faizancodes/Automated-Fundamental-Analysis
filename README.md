# Automated Fundamental Analysis via Python

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

A lightweight, open‑source tool that grades every US‑listed stock on **Finviz** using a statistically‑driven scoring system. Each stock receives a rating out of **100** based on four categories:

- **Valuation**
- **Profitability**
- **Growth**
- **Price Performance**

The project ships with two ways to explore the data:

1. **Command‑line script** (`stockgrader.py`) – scrapes ~8,300 stocks, computes scores, and writes a CSV file.
2. **Streamlit web app** (`WebApp/app.py`) – visualises the results interactively.

---

## Table of Contents

- [Installation](#installation)
- [Running the CLI](#running-the-cli)
- [Running the Web App](#running-the-web-app)
- [Output Format](#output-format)
- [Grading System Explained](#grading-system-explained)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/faizancodes/Automated-Fundamental-Analysis.git
cd Automated-Fundamental-Analysis

# 2️⃣ Install dependencies (Python 3.10+ recommended)
pip install -r requirements.txt
```

> **Tip:** Use a virtual environment (`venv` or `conda`) to keep dependencies isolated.

---

## Running the CLI

The command‑line interface scrapes data from Finviz, grades each stock, and creates a CSV file in the project root.

```bash
python stockgrader.py
```

When the script finishes you will see a file similar to `StockRatings-04.05.22.csv`. The CSV contains the following columns (excerpt):

| Symbol | Sector | Valuation | Profitability | Growth | Price Performance | Overall Score |
|--------|--------|-----------|---------------|--------|-------------------|---------------|
| AAPL   | Technology | 85 | 90 | 78 | 88 | 85 |

You can open the CSV with Excel, Google Sheets, or any data‑analysis tool.

---

## Running the Web App

The Streamlit app provides an interactive dashboard to explore the generated ratings.

```bash
# Navigate to the web‑app folder
cd WebApp

# Launch the app (default port 8501)
streamlit run app.py
# or, on Windows without the `streamlit` command in PATH:
py -m streamlit run app.py
```

Open your browser and go to `http://localhost:8501` (or the URL shown in the terminal).

---

## Output Format

The CSV file contains one row per stock with the following fields:

- **Ticker** – Stock ticker symbol.
- **Sector** – Industry sector as defined by Finviz.
- **Valuation, Profitability, Growth, Price Performance** – Individual category scores (0‑100).
- **Overall Score** – Weighted average of the four categories, also on a 0‑100 scale.

You can filter, sort, or visualise the data to discover undervalued or high‑quality stocks.

---

## Grading System Explained

The scoring algorithm is based on the **percentile** of a metric within its sector:

1. For each metric (e.g., Net Margin) the program collects values for **all** stocks in the same sector.
2. Outliers are removed, then the **standard deviation** of the cleaned set is calculated.
3. The standard deviation is divided by three to obtain a *"Change"* value – the step size for grading.
4. A stock’s metric is compared to the sector’s distribution:
   - If the metric is **higher** than the sector average, each *"Change"* step above the mean adds a grade increment (A+, A, A‑, …).
   - For metrics where **lower** is better (e.g., P/E), the 10th percentile is used as the reference point.

The figure below illustrates the grading curve for a metric where higher is better:

![Grading Curve](https://user-images.githubusercontent.com/43652410/98454501-06703e00-2133-11eb-8521-c5c532a759c1.png){: width="500" height="400" alt="Grading curve"}

And an example of how the final rating is derived from the four category scores:

![Overall Rating Calculation](https://user-images.githubusercontent.com/43652410/98454570-f442cf80-2133-11eb-8a3a-cee8da8a3f59.jpg){: width="650" height="500" alt="Overall rating"}

---

## Screenshots

| CLI Output | Web App Dashboard |
|------------|-------------------|
| <img src="https://user-images.githubusercontent.com/43652410/161826590-455f2d30-5605-42c5-a8c1-2c1c75d03d26.png" width="750" height="900"> | <img src="https://user-images.githubusercontent.com/43652410/161826910-83856a1c-e7d2-454c-b0df-1bb06251d3f7.png" width="750" height="900"> |

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

Typical workflow:

```bash
# Fork the repo and clone your fork
git clone https://github.com/<your‑username>/Automated-Fundamental-Analysis.git
cd Automated-Fundamental-Analysis

# Create a new branch for your feature/fix
git checkout -b my‑feature

# Make changes, then commit & push
git commit -am "Add new feature"
git push origin my‑feature

# Open a Pull Request on GitHub
```

Please ensure that any new code follows the existing style and includes appropriate docstrings.

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.
