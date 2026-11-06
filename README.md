[README.md](https://github.com/user-attachments/files/34483519/README.md)
# FactoryMind --- AI-Powered Predictive Maintenance

[![FactoryMind Dashboard Demo](https://img.youtube.com/vi/E5j8p402l0k/0.jpg)](https://www.youtube.com/watch?v=E5j8p402l0k)

*Click the preview to watch the dashboard demonstration.*

FactoryMind is an end-to-end predictive-maintenance prototype that
combines machine-learning-based failure-risk estimation with sensor-data
validation, an API-backed data layer, workflow orchestration, and
retrieval-augmented maintenance assistance.

The project demonstrates how an ML model can be integrated into a larger
application workflow rather than being used only in a notebook.

> **Project status:** Working portfolio prototype. Docker configuration
> is included in the repository, but containerized deployment should be
> treated as unverified until the Compose stack has been built and
> tested on a clean environment.

## At a glance

-   **Problem:** Identify elevated machine-failure risk from
    operating-condition and tool-wear measurements.
-   **Dataset:** AI4I 2020 predictive-maintenance dataset (10,000
    records; approximately 3.39% machine-failure cases).
-   **ML task:** Binary classification --- machine failure / no machine
    failure.
-   **Backend:** FastAPI and SQLAlchemy with PostgreSQL persistence.
-   **Workflow:** LangGraph-based assessment flow.
-   **Maintenance assistant:** Retrieval-augmented generation (RAG) over
    a maintenance manual, using ChromaDB, Sentence Transformers
    embeddings, and Gemini for answer generation.
-   **Interface:** Streamlit dashboard.

## Demo

Add short recordings here after recording and reviewing the actual
application:

-   **Dashboard walkthrough:** [Watch Video](https://youtu.be/E5j8p402l0k)
-   **Machine assessment:** [Watch Video](https://youtu.be/gQA4lVdX3LA)
-   **Maintenance assistant:** [Watch Video](https://youtu.be/TwZrUYr7m5I)
-   **Machine History:** [Watch Video](https://youtu.be/XZ-x3LGaEoQ)


For the GitHub README, use a clickable thumbnail that links to the
hosted video, or a GitHub-hosted attachment. Avoid committing large raw
video files into the repository history.

## Features

### 1. Sensor-data validation

-   Validates required sensor fields and numeric values.
-   Rejects invalid values, including non-finite numeric values.
-   Applies configured sensor-range checks.
-   Returns structured validation information for downstream processing.

### 2. Failure-risk prediction

-   Uses the AI4I 2020 dataset for model development.
-   Uses five operating-condition features:
    -   Air temperature (K)
    -   Process temperature (K)
    -   Rotational speed (rpm)
    -   Torque (Nm)
    -   Tool wear (min)
-   Compares candidate classifiers, including Logistic Regression,
    class-weighted Logistic Regression, and Random Forest.
-   Uses stratified train, validation, and test partitions.
-   Saves the selected preprocessing/model pipeline and metadata under
    `artifacts/`.

The model is a risk-estimation component, not a guarantee that a machine
will or will not fail.

### 3. API and persistence

FastAPI exposes endpoints for prediction, machine assessment, machine
history, machine inventory, dashboard summaries, and maintenance
questions.

SQLAlchemy models persist machine information, sensor readings, and
prediction results in PostgreSQL.

### 4. LangGraph assessment workflow

The assessment workflow coordinates the application steps, including
machine validation, prediction, history retrieval, and
maintenance-response generation when relevant.

### 5. RAG-based maintenance assistant

The RAG pipeline:

1.  Loads and extracts text from a maintenance PDF.
2.  Cleans and splits the extracted text into chunks.
3.  Generates embeddings using Sentence Transformers.
4.  Stores and retrieves document chunks using ChromaDB.
5.  Uses Gemini to generate a response grounded in retrieved context.

The included manual is for a specific SureServo AC servo system. The
assistant's answers should therefore be interpreted in the context of
that manual, not as universal guidance for every machine.

### 6. Streamlit dashboard

The dashboard provides views for:

-   Overall system summary and machine inventory
-   Machine assessment
-   Machine prediction history
-   Maintenance questions and answers

## Architecture

``` text
                         ┌────────────────────────┐
                         │   Streamlit Dashboard  │
                         │       frontend/        │
                         └───────────┬────────────┘
                                     │ HTTP
                                     ▼
                         ┌────────────────────────┐
                         │       FastAPI          │
                         │        app/main.py     │
                         └───────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │  ML Model Service│   │ LangGraph Agents │   │   RAG Pipeline   │
   │  model_service.py│   │ agents/          │   │      rag/        │
   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
            │                      │                      │
            │                      ├── Prediction/history │
            │                      └── Maintenance answer │
            │                                             ▼
            │                                  ┌────────────────────┐
            │                                  │ ChromaDB + Manual  │
            │                                  │ Embeddings + Gemini│
            │                                  └────────────────────┘
            │
            ▼
   ┌────────────────────────────────────────────────────────┐
   │ PostgreSQL                                              │
   │ Machines · Sensor readings · Prediction records         │
   └────────────────────────────────────────────────────────┘
```

## Machine-learning methodology

### Dataset and target

The project uses the AI4I 2020 Predictive Maintenance dataset. The
target is `Machine failure`.

The model uses these five input features:

  Feature               Unit
  --------------------- ------
  Air temperature       K
  Process temperature   K
  Rotational speed      rpm
  Torque                Nm
  Tool wear             min

Identifier columns and direct failure-mode indicator columns are
excluded from the model feature set to avoid target leakage.

### Class imbalance

The dataset is imbalanced: approximately 3.39% of records represent
machine failures. Accuracy alone can therefore give a misleading
impression of model quality.

Evaluation should emphasize:

-   **Recall:** How many actual failure cases are detected.
-   **Precision:** How many predicted failures are actual failures.
-   **F1-score:** Balance between precision and recall.
-   **PR-AUC:** Ranking performance for the minority class.
-   **Confusion matrix:** False negatives and false positives.

### Validation experiment

During threshold experimentation on the validation partition, a
threshold of 0.2 produced:

  Metric        Validation result
  ----------- -------------------
  Precision                42.31%
  Recall                   43.14%
  F1-score                 42.72%

These are **validation results from a threshold experiment**, not final
held-out test results and not a claim of production performance. The
threshold used by the saved application artifact should be checked
against `artifacts/model_metadata.json` and the current
prediction-service implementation.

Add the final held-out test metrics here after confirming them from a
fresh run of the training/evaluation pipeline:

  Test metric     Result
  ------------- --------
  Precision         TODO
  Recall            TODO
  F1-score          TODO
  PR-AUC            TODO

Do not substitute validation metrics for test metrics.

## Technology stack

  -----------------------------------------------------------------------
  Area                                Technologies
  ----------------------------------- -----------------------------------
  Language                            Python

  Data processing                     pandas, NumPy

  Machine learning                    scikit-learn, joblib

  API                                 FastAPI, Pydantic, Uvicorn

  Database                            PostgreSQL, SQLAlchemy, psycopg

  Workflow orchestration              LangGraph

  Retrieval and vector storage        ChromaDB, Sentence Transformers

  Answer generation                   Google Gemini

  Dashboard                           Streamlit

  Testing                             pytest

  Containerization                    Docker, Docker Compose
                                      (configuration included; verify
                                      before relying on it)
  -----------------------------------------------------------------------

## Repository structure

``` text
FactoryMind/
├── app/
│   ├── agents/             # LangGraph state, nodes and graph
│   ├── rag/                # Document ingestion, chunking, embeddings and retrieval
│   ├── crud.py             # Database operations
│   ├── database.py         # SQLAlchemy engine and session setup
│   ├── main.py             # FastAPI application and routes
│   ├── model_service.py    # Model loading and prediction
│   ├── models.py           # SQLAlchemy models
│   └── schemas.py          # Request and response schemas
├── artifacts/              # Trained model and metadata
├── data/manuals/           # Maintenance reference manual
├── frontend/               # Streamlit dashboard
├── tests/                  # Automated tests
├── Notebooks Experiment/   # Model development and exploration notebooks
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Getting started (local development)

### Prerequisites

-   Python 3.13
-   PostgreSQL
-   A Google Gemini API key for the maintenance-answer generation
    component
-   Git

### 1. Clone the repository

``` bash
git clone https://github.com/sarasayed7/FactoryMind---AI-powered-Predictive-Maintenance-System.git
cd FactoryMind---AI-powered-Predictive-Maintenance-System
```

### 2. Create and activate a virtual environment

Windows PowerShell:

``` powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

``` bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your local PostgreSQL
credentials and Gemini configuration.

Windows PowerShell:

``` powershell
Copy-Item .env.example .env
```

macOS / Linux:

``` bash
cp .env.example .env
```

Never commit `.env` or paste API keys into source files.

### 5. Prepare PostgreSQL

Create a PostgreSQL database and configure the connection values in
`.env`. Ensure the environment-variable names match those read by
`app/database.py`.

The application expects the database schema and machine records to be
initialized. Follow the initialization logic currently present in the
application before making API requests.

### 6. Run the backend

``` bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

### 7. Run the Streamlit dashboard

In a second terminal, activate the same virtual environment and run:

``` bash
streamlit run frontend/dashboard.py
```

The dashboard's API URL should point to the local backend
(`http://127.0.0.1:8000`) unless configured otherwise.

## API overview

The current application exposes these routes:

  ----------------------------------------------------------------------------------
  Method                  Endpoint                           Purpose
  ----------------------- ---------------------------------- -----------------------
  `GET`                   `/health`                          Health check

  `POST`                  `/predict`                         Generate and persist a
                                                             machine-failure
                                                             prediction

  `GET`                   `/machines`                        List registered
                                                             machines

  `GET`                   `/machines/{machine_id}/history`   Retrieve a machine's
                                                             prediction/readings
                                                             history

  `POST`                  `/machines/{machine_id}/assess`    Run the coordinated
                                                             machine-assessment
                                                             workflow

  `GET`                   `/dashboard/summary`               Retrieve dashboard
                                                             summary data

  `POST`                  `/maintenance/ask`                 Ask a maintenance
                                                             question using the RAG
                                                             pipeline
  ----------------------------------------------------------------------------------

For request and response schemas, use the live Swagger documentation at
`/docs`.

## Testing

Run the test suite from the repository root:

``` bash
pytest -q
```

The repository includes API, schema, assessment, graph, and routing
tests. Test results can depend on local database configuration and
external service settings; configure the required test environment
before running them.

## Docker

A `Dockerfile` and `docker-compose.yml` are included. The containerized
setup should be considered **under verification** until it has been
built and tested from a clean environment.

Once verified, add the exact Compose startup instructions and document
the persistent PostgreSQL and ChromaDB volumes here. Do not assume that
local PostgreSQL data is copied into a new container volume.

### 1. Clone the repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FactoryMind---AI-powered-Predictive-Maintenance-System
```

### 2. Create environment configuration
copy .env.example .env

### 3. Configure the required environment variables in .env

### 4. Build and start all services
```bash
docker compose up --build
```

## Limitations and responsible use

-   AI4I 2020 is a synthetic dataset; results may not generalize to real
    industrial equipment or operating environments.
-   The model estimates risk from a limited set of sensor features. It
    is not a certified safety system and must not be used as the sole
    basis for operational or maintenance decisions.
-   False negatives can be costly. Threshold selection should reflect
    the application's risk tolerance and be validated with domain
    experts.
-   The maintenance assistant is grounded in the included SureServo
    manual. Its responses are limited by the manual's coverage and
    retrieval quality.
-   Gemini-based answer generation requires a valid API key and network
    access.
-   The current project is a portfolio prototype, not a validated
    production deployment.

## Future improvements

-   Complete and verify Docker Compose deployment.
-   Add CI checks for linting, tests, and dependency/security scanning.
-   Add model-version tracking and repeatable evaluation reports.
-   Evaluate retrieval quality and answer faithfulness on a curated
    maintenance-question set.
-   Add monitoring for prediction distribution, data drift, and model
    performance.
-   Validate the system against real, domain-approved machine data
    before any operational use.

## Author

**Sara Sayed**

-   GitHub: [@sarasayed7](https://github.com/sarasayed7)
-   Project repository:
    [FactoryMind](https://github.com/sarasayed7/FactoryMind---AI-powered-Predictive-Maintenance-System)

------------------------------------------------------------------------

If you find an issue or have a suggestion, please open a GitHub issue.
