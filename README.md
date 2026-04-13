# QueryMind — Natural Language to SQL

Ask your PostgreSQL database questions in plain English. QueryMind converts them to SQL using a local AI model, executes them, and displays the results — all in a chatbot-style interface.

![Dark Theme](https://img.shields.io/badge/theme-dark%20%7C%20light-00e676?style=flat-square)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat-square&logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)

---

## Features

- **Natural language queries** — type a question, get SQL back instantly
- **Live schema introspection** — your real table structure is used in the prompt automatically
- **Chat history** — full conversation per session, up to 20 messages
- **Split-screen layout** — chat on the left, live results on the right
- **Dashboard & Excel views** — spacious dashboard table by default, toggle to dense Excel view
- **Collapsible schema browser** — browse all tables and column types in the sidebar
- **Dark / Light mode** — persisted in localStorage
- **Safety** — only SELECT queries are executed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0 |
| AI Model | [NumbersStation/nsql-350M](https://huggingface.co/NumbersStation/nsql-350M) via HuggingFace Transformers |
| Database (sessions) | SQLite |
| Target Database | PostgreSQL (user-supplied at runtime) |
| DB Driver | psycopg2 |

---

## Setup

**1. Clone and install dependencies**
```bash
git clone <repo-url>
cd natural-language-to-sql-query-convertor
pip install django psycopg2-binary transformers torch django-environ
```

**2. Run migrations** (creates the SQLite session database)
```bash
python manage.py migrate
```

**3. Start the server**
```bash
python manage.py runserver
```

**4. Open** `http://localhost:8000` and enter your PostgreSQL credentials.

> **Note:** The AI model (~700 MB) is downloaded from HuggingFace automatically on the first query. Subsequent queries are fast.

---

## Model Alternatives

The default model (`nsql-350M`) is lightweight and runs on CPU. To use a more accurate model, change `MODEL_NAME` in `query/query_app/model_utils.py`:

| Model | Size | Notes |
|---|---|---|
| `NumbersStation/nsql-350M` | ~700 MB | Default, CPU-friendly |
| `NumbersStation/nsql-6B` | ~12 GB | Much better accuracy |
| `NumbersStation/nsql-llama-2-7B` | ~14 GB | Llama 2 based |
| `defog/sqlcoder-7b-2` | ~14 GB | State-of-the-art open source |

---

## Project Structure

```
query/
├── query/              # Django project config (settings, urls)
├── query_app/
│   ├── views.py        # connect, query, disconnect views + chat history
│   ├── model_utils.py  # SQLModel — wraps nsql-350M, builds schema prompt
│   ├── db_utils.py     # test_connection, get_schema, execute_query
│   └── forms.py        # ConnectionForm
└── template/
    ├── base.html       # Theme tokens, fonts, shared scripts
    ├── connect.html    # Split-screen connection page
    └── query.html      # Chat interface + output panel
```

---

## How It Works

1. User connects with PostgreSQL credentials → stored in Django session
2. On each query, `db_utils.get_schema()` fetches live table/column info via `information_schema`
3. Schema is formatted as `CREATE TABLE` statements and passed to `nsql-350M` along with the NL question
4. Model generates SQL; only the new tokens (not the prompt) are decoded
5. SQL is validated (must be SELECT), executed via `psycopg2`, and results are returned
