# Data Science / Machine Learning Project

A complete data science project template for machine learning model development, training, evaluation, and deployment.

## Overview

This project provides a structured framework for:
- Data collection and preprocessing
- Exploratory Data Analysis (EDA)
- Feature engineering
- Model training and evaluation
- Hyperparameter tuning
- Model deployment and serving
- MLOps and monitoring

## Tech Stack

### Core Libraries
- **Python 3.10+** - Programming language
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Data visualization
- **Scikit-learn** - Machine learning

### Deep Learning (Optional)
- **TensorFlow** - Deep learning framework
- **PyTorch** - Deep learning framework
- **Keras** - High-level neural networks API

### Data Processing
- **Jupyter/JupyterLab** - Interactive notebooks
- **Polars** - Fast DataFrame library (alternative to Pandas)
- **Dask** - Parallel computing for large datasets

### MLOps
- **MLflow** - Experiment tracking and model registry
- **DVC** - Data version control
- **FastAPI** - Model serving API
- **Docker** - Containerization

### Database
- **PostgreSQL** - Relational database
- **Redis** - Caching and feature store

## Features

- Data ingestion and validation
- Exploratory Data Analysis (EDA)
- Feature engineering pipeline
- Model training with cross-validation
- Hyperparameter optimization
- Model evaluation and comparison
- Model versioning and registry
- RESTful API for model serving
- Automated testing
- CI/CD pipeline
- Model monitoring and drift detection

## Getting Started

### Prerequisites

- Python 3.10+
- pip or conda
- Virtual environment tool (venv, conda)
- Git
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Or using conda
   conda create -n ml-project python=3.10
   conda activate ml-project
   ```

3. **Install dependencies**
   ```bash
   # Core dependencies
   pip install -r requirements.txt

   # Development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Download data** (if applicable)
   ```bash
   # Using DVC
   dvc pull

   # Or download manually
   python scripts/download_data.py
   ```

## Project Structure

```
.
├── data/                      # Data directory (not in git)
│   ├── raw/                  # Raw, immutable data
│   ├── interim/              # Intermediate processed data
│   ├── processed/            # Final processed data
│   └── external/             # External data sources
│
├── notebooks/                 # Jupyter notebooks
│   ├── 01_eda.ipynb         # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_evaluation.ipynb
│
├── src/                      # Source code
│   ├── data/                # Data processing
│   │   ├── load.py         # Data loading
│   │   ├── clean.py        # Data cleaning
│   │   └── transform.py    # Data transformation
│   │
│   ├── features/            # Feature engineering
│   │   ├── build.py        # Feature building
│   │   └── selection.py    # Feature selection
│   │
│   ├── models/              # Model code
│   │   ├── train.py        # Model training
│   │   ├── predict.py      # Predictions
│   │   └── evaluate.py     # Evaluation metrics
│   │
│   ├── api/                 # Model serving API
│   │   ├── main.py         # FastAPI application
│   │   └── schemas.py      # API schemas
│   │
│   └── utils/              # Utility functions
│       ├── config.py       # Configuration
│       └── logging.py      # Logging setup
│
├── models/                   # Trained models (not in git)
│   ├── model_v1.pkl
│   └── model_v2.pkl
│
├── tests/                    # Test suite
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
│
├── scripts/                  # Utility scripts
│   ├── download_data.py
│   ├── train_model.py
│   └── evaluate_model.py
│
├── mlruns/                   # MLflow tracking (not in git)
├── docker/                   # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .dvc/                     # DVC configuration
├── dvc.yaml                 # DVC pipeline
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

## Data Pipeline

### 1. Data Loading

```python
# src/data/load.py
import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """Load data from CSV file."""
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df
```

### 2. Data Cleaning

```python
# src/data/clean.py
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess data."""
    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))

    # Remove outliers
    df = remove_outliers(df)

    return df
```

### 3. Feature Engineering

```python
# src/features/build.py
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create new features."""
    # Create derived features
    df['feature_ratio'] = df['feature_a'] / df['feature_b']
    df['feature_interaction'] = df['feature_a'] * df['feature_b']

    # Encode categorical variables
    df = pd.get_dummies(df, columns=['category'], drop_first=True)

    return df
```

## Model Development

### Training Script

```python
# src/models/train.py
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

def train_model(X, y):
    """Train machine learning model."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Start MLflow run
    with mlflow.start_run():
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Log metrics
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)

        # Save model
        mlflow.sklearn.log_model(model, "model")

    return model
```

### Hyperparameter Tuning

```python
# src/models/tune.py
from sklearn.model_selection import GridSearchCV

def tune_hyperparameters(X, y):
    """Optimize model hyperparameters."""
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
    }

    model = RandomForestClassifier(random_state=42)

    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=5,
        scoring='f1_weighted',
        n_jobs=-1
    )

    grid_search.fit(X, y)

    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_
```

## Model Serving API

### FastAPI Application

```python
# src/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ML Model API")

# Load model at startup
model = joblib.load("models/model_v1.pkl")

class PredictionInput(BaseModel):
    features: list[float]

class PredictionOutput(BaseModel):
    prediction: int
    probability: float

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """Make prediction."""
    features = np.array(input_data.features).reshape(1, -1)
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0].max()

    return PredictionOutput(
        prediction=int(prediction),
        probability=float(probability)
    )

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### Running the API

```bash
# Start API server
uvicorn src.api.main:app --reload --port 8000

# Access API docs
open http://localhost:8000/docs
```

## Running Experiments

### Command Line

```bash
# Train model
python scripts/train_model.py --data data/processed/train.csv

# Evaluate model
python scripts/evaluate_model.py --model models/model_v1.pkl

# Make predictions
python scripts/predict.py --model models/model_v1.pkl --data data/test.csv
```

### Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Or Jupyter Notebook
jupyter notebook
```

### MLflow Tracking

```bash
# Start MLflow UI
mlflow ui --port 5000

# View experiments
open http://localhost:5000
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py
```

### Example Test

```python
# tests/test_models.py
import pytest
from src.models.train import train_model
import pandas as pd
import numpy as np

def test_model_training():
    """Test model training."""
    # Create sample data
    X = np.random.rand(100, 5)
    y = np.random.randint(0, 2, 100)

    # Train model
    model = train_model(X, y)

    # Test prediction
    prediction = model.predict(X[:1])
    assert prediction.shape == (1,)
    assert prediction[0] in [0, 1]
```

## DVC Pipeline

### Define Pipeline

```yaml
# dvc.yaml
stages:
  load_data:
    cmd: python src/data/load.py
    deps:
      - data/raw/data.csv
    outs:
      - data/interim/loaded_data.csv

  preprocess:
    cmd: python src/data/clean.py
    deps:
      - data/interim/loaded_data.csv
    outs:
      - data/processed/clean_data.csv

  train:
    cmd: python src/models/train.py
    deps:
      - data/processed/clean_data.csv
      - src/models/train.py
    outs:
      - models/model.pkl
    metrics:
      - metrics/train_metrics.json
```

### Run Pipeline

```bash
# Run entire pipeline
dvc repro

# Run specific stage
dvc repro train
```

## Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY models/ models/

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build image
docker build -t ml-model-api .

# Run container
docker run -p 8000:8000 ml-model-api
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models/model.pkl
    volumes:
      - ./models:/app/models
```

## Monitoring

### Model Performance Monitoring

```python
# src/monitoring/drift.py
from scipy.stats import ks_2samp

def detect_data_drift(reference_data, current_data, threshold=0.05):
    """Detect data drift using Kolmogorov-Smirnov test."""
    for column in reference_data.columns:
        statistic, p_value = ks_2samp(
            reference_data[column],
            current_data[column]
        )
        if p_value < threshold:
            print(f"Drift detected in {column}: p-value={p_value:.4f}")
            return True
    return False
```

## Best Practices

### Code Organization
- Keep notebooks for exploration, scripts for production
- Use relative imports within the project
- Follow PEP 8 style guide
- Document functions with docstrings

### Data Management
- Never commit raw data to git
- Use DVC for data version control
- Keep data pipeline reproducible
- Document data sources and schemas

### Model Development
- Track all experiments with MLflow
- Use cross-validation for model selection
- Save preprocessing steps with the model
- Version your models

### Testing
- Write unit tests for critical functions
- Test data validation logic
- Test feature engineering functions
- Use fixtures for test data

## Environment Variables

```bash
# .env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ml_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# Model
MODEL_PATH=models/model_v1.pkl

# API
API_KEY=your-api-key-here
```

## Resources

### Documentation
- [Scikit-learn](https://scikit-learn.org/)
- [Pandas](https://pandas.pydata.org/)
- [MLflow](https://mlflow.org/)
- [DVC](https://dvc.org/)

### Books
- "Hands-On Machine Learning" by Aurélien Géron
- "Python Data Science Handbook" by Jake VanderPlas
- "Feature Engineering for Machine Learning" by Alice Zheng

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and ensure they pass
6. Submit a pull request

## License

[Your License Here]

## Support

- Documentation: [Your docs URL]
- Issues: [GitHub Issues]
- Email: ml-support@your-company.com

---

**Built with Claude Code Generator** - Data science workflows, simplified.
