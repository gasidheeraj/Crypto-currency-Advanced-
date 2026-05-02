# Cryptocurrency Volatility Forecasting

> **An end-to-end machine learning platform for next-day cryptocurrency price and volatility forecasting, powered by a production-grade ETL pipeline, an ensemble of supervised learning models, and an interactive analytics dashboard.**

---

## Overview

Cryptocurrency markets are characterized by extreme volatility, non-stationary price behavior, and a high signal-to-noise ratio that renders traditional forecasting techniques unreliable. This project addresses that challenge by delivering a **fully automated, modular forecasting system** that ingests live market data, engineers domain-aware features, trains a hybrid ensemble of regression models, and surfaces predictions through a real-time analytics dashboard.

The platform is designed around three engineering principles: **reproducibility** (deterministic pipelines and persisted models), **scalability** (a multi-asset training framework that generalizes to any cryptocurrency), and **observability** (structured logging and execution tracking at every stage).

---

## Key Features

- **Production-Grade ETL Pipeline** — A modular Extract–Transform–Load architecture that pulls live market data from the **CoinGecko REST API**, applies validation and normalization, and persists the results to a **PostgreSQL** relational store.
- **Automated Scheduling Layer** — Configurable interval-based and cron-style scheduling (every minute, every 10 minutes, hourly, daily) ensures the data warehouse remains continuously synchronized with the market.
- **Historical Backfill Module** — A dedicated ingestion script for bootstrapping the database with historical OHLC data, enabling robust model training from day one.
- **Domain-Aware Feature Engineering** — A rich feature set including lagged prices, rolling moving averages, multi-period momentum, rolling volatility, and classical technical indicators such as **RSI** and **MACD**.
- **Hybrid Ensemble Forecasting Model** — A weighted ensemble that combines **Ridge Regression** (linear baseline), **Random Forest Regressor** (non-linear pattern capture), and **XGBoost** (gradient-boosted residual correction), with weights dynamically derived from each learner's out-of-sample R² score.
- **Multi-Asset Training Framework** — A single command trains independent ensemble models for every cryptocurrency in the catalog, with per-asset metrics and persisted artifacts.
- **Interactive Streamlit Dashboard** — A web-based interface for exploring price history, technical indicators, and forecast outputs, built with Streamlit and Plotly.
- **Diagnostic Tooling** — A dedicated diagnostic script for inspecting predictions, validating model behavior, and surfacing anomalies before deployment.
- **Structured Observability** — Centralized logging via **Loguru**, with every pipeline run recorded in an execution-tracking table (status, record counts, runtime, error context).

---

## System Architecture

The codebase is organized as a layered, separation-of-concerns architecture in which each subsystem is independently testable and swappable.

```
Cryptocurrency-Volatility-Forecasting/
├── main.py                          # ETL pipeline orchestrator
├── automated_pipeline.py            # Scheduler for continuous data ingestion
├── collect_historical_data.py       # Historical backfill ingestion script
├── update_daily_prices.py           # Daily incremental price update routine
├── train_hybrid_model.py            # Single-asset ensemble training (Bitcoin)
├── train_all_hybrid_models.py       # Multi-asset ensemble training driver
├── diagnose_prediction.py           # Model diagnostics & sanity checks
├── requirements.txt                 # Pinned dependency manifest
│
├── data_engineering/                # ETL subsystem
│   ├── config/                      # Database & environment configuration
│   ├── pipelines/
│   │   ├── extract/                 # CoinGecko API extractor
│   │   ├── transform/               # Validation & normalization layer
│   │   └── load/                    # PostgreSQL loader & execution logger
│   └── utils/                       # Logging utilities
│
├── data_science/                    # ML & analytics subsystem
│   ├── indicators/                  # Technical indicator computation (RSI, MACD, etc.)
│   └── utils/                       # Data loaders for model training
│
├── database/
│   └── schemas/                     # DDL scripts (table creation, seed data)
│
├── models/
│   └── saved/                       # Persisted ensemble model artifacts (.pkl)
│
└── dashboard/                       # Streamlit-based analytics frontend
```

### Data Flow

```
   ┌────────────────┐      ┌─────────────────┐      ┌──────────────────┐
   │  CoinGecko API │ ───▶ │   ETL Pipeline  │ ───▶ │   PostgreSQL DB  │
   └────────────────┘      └─────────────────┘      └──────────────────┘
                                                              │
                                                              ▼
   ┌────────────────┐      ┌─────────────────┐      ┌──────────────────┐
   │ Streamlit UI   │ ◀─── │ Trained Models  │ ◀─── │ Feature Pipeline │
   └────────────────┘      └─────────────────┘      └──────────────────┘
```

---

## Modeling Approach

Forecasting cryptocurrency prices is a notoriously difficult regression problem due to the random-walk nature of asset returns. To mitigate this, the system adopts a **hybrid ensemble strategy** that combines complementary learners:

| Component               | Role                                                        | Strength                                              |
| ----------------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| **Ridge Regression**    | Linear baseline that anchors predictions to recent history. | Stable, low-variance, exploits the strong autoregressive signal in daily prices. |
| **Random Forest**       | Non-linear ensemble of decision trees.                      | Captures regime shifts and interaction effects between technical indicators. |
| **XGBoost**             | Gradient-boosted tree ensemble.                             | Iteratively corrects residual errors and handles heterogeneous feature scales. |

The final prediction is a **weighted average** of the three learners, where each weight is proportional to that learner's out-of-sample R² score on the held-out test set. This dynamic weighting ensures the ensemble adapts to whichever model performs best for a given asset, rather than relying on a single fixed strategy.

### Feature Engineering

The feature pipeline transforms raw price series into a model-ready matrix containing:

- **Lagged prices** at offsets of 1, 2, 3, 5, and 7 days.
- **Simple moving averages** over 7-, 14-, and 30-day windows.
- **Momentum** (percentage change) over 3-, 7-, and 14-day periods.
- **Rolling volatility** computed as the 7-day standard deviation.
- **Relative Strength Index (RSI)** — a bounded oscillator quantifying overbought/oversold regimes.
- **Moving Average Convergence Divergence (MACD)** — a trend-following momentum indicator.

### Evaluation Metrics

Every trained model is evaluated on a chronological **80/20 train-test split** (no shuffling, to preserve temporal causality) using the following metrics:

- **R² (Coefficient of Determination)** — proportion of variance explained.
- **MAE (Mean Absolute Error)** — average dollar error per prediction.
- **RMSE (Root Mean Squared Error)** — penalizes large deviations more heavily.
- **MAPE (Mean Absolute Percentage Error)** — scale-independent error metric.
- **Directional Accuracy** — derived as `100 − MAPE`, expressed as a percentage.

---

## Tech Stack

| Layer                     | Technology                                                   |
| ------------------------- | ------------------------------------------------------------ |
| **Language**              | Python 3.10+                                                 |
| **Data Source**           | CoinGecko REST API                                           |
| **Database**              | PostgreSQL (via `psycopg2`)                                  |
| **Data Validation**       | Pydantic                                                     |
| **Numerical Computing**   | NumPy                                                        |
| **Machine Learning**      | scikit-learn, XGBoost                                        |
| **Model Persistence**     | Joblib                                                       |
| **Scheduling**            | `schedule` library                                           |
| **Logging**               | Loguru                                                       |
| **Visualization**         | Streamlit, Plotly, Matplotlib, Seaborn                       |
| **HTTP Client**           | Requests, aiohttp                                            |
| **Configuration**         | python-dotenv, PyYAML                                        |
| **Testing**               | pytest, pytest-cov                                           |

---

## Getting Started

### Prerequisites

- Python **3.10** or later
- A running **PostgreSQL** instance (local or remote)
- A **CoinGecko API** key (the free tier is sufficient for development)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/gasidheeraj/Cryptocurrency-Volatility-Forecasting.git
cd Cryptocurrency-Volatility-Forecasting

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with your database credentials and API keys:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crypto_db
DB_USER=postgres
DB_PASSWORD=your_password

COINGECKO_API_KEY=your_api_key
```

### Usage

#### 1. Initialize the Database and Run the ETL Pipeline

```bash
python main.py
```

This bootstraps the schema, seeds the cryptocurrency catalog, and executes one full Extract–Transform–Load cycle.

#### 2. Backfill Historical Data

```bash
python collect_historical_data.py
```

#### 3. Run the Pipeline on a Schedule

```bash
python automated_pipeline.py
```

The scheduler will run the ingestion job at multiple cadences (every minute, every 10 minutes, hourly, and daily at 09:00). Press `Ctrl+C` to stop.

#### 4. Train Forecasting Models

Train an ensemble for a single asset (Bitcoin):

```bash
python train_hybrid_model.py
```

Train ensembles for **all** cryptocurrencies in the catalog:

```bash
python train_all_hybrid_models.py
```

Trained model artifacts are persisted to `models/saved/` as `.pkl` files.

#### 5. Diagnose Predictions

```bash
python diagnose_prediction.py
```

#### 6. Launch the Dashboard

```bash
streamlit run dashboard/<entry_point>.py
```

---

## Project Highlights

- **End-to-End Ownership** — Designed and implemented every layer from API ingestion to model serving and visualization.
- **Production-Ready Engineering** — Structured logging, execution tracking, error handling, and pipeline observability built in from the start.
- **Empirically Grounded ML** — Ensemble weights derived from out-of-sample performance rather than arbitrary tuning, and evaluation conducted on chronologically split data to respect time-series causality.
- **Generalizable Framework** — The same training driver scales from a single asset to the entire catalog without code changes.
- **Modular & Extensible** — Each subsystem (extract, transform, load, indicators, models, dashboard) is decoupled and independently replaceable.

---

## Roadmap

- [ ] Integration of **deep learning architectures** (LSTM, Temporal Convolutional Networks) for sequence modeling.
- [ ] Incorporation of **alternative data sources** — on-chain metrics, order-book depth, social sentiment.
- [ ] **Hyperparameter optimization** via Optuna or Bayesian search.
- [ ] **Containerization** with Docker and orchestration via Apache Airflow.
- [ ] **Walk-forward validation** and backtesting framework with realistic transaction costs.
- [ ] **REST API layer** (FastAPI) for serving predictions to downstream consumers.
- [ ] **CI/CD pipeline** with automated testing, linting, and model retraining triggers.

---

## Author

**Sai Dheeraj G**
GitHub: [@gasidheeraj](https://github.com/gasidheeraj)

