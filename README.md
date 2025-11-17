# Credit Risk AI – Production-Grade ML System  
![Python](https://img.shields.io/badge/python-3.11-blue)  
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)  
![XGBoost](https://img.shields.io/badge/XGBoost-AUC%200.782-orange)  
![SHAP](https://img.shields.io/badge/SHAP-Explainable_AI-red)  
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-yellow)

**A bank-grade credit risk model** that predicts loan default probability using **XGBoost**, **Optuna**, and **SHAP**, deployed via **FastAPI** and **Streamlit**.

---

## Features

| Feature | Status |
|-------|--------|
| **XGBoost + Optuna Tuning** | 30 trials → **AUC 0.782** |
| **SHAP Explanations** | Per-loan waterfall plots |
| **FastAPI Inference** | Real-time `/predict` endpoint |
| **Streamlit Dashboard** | Interactive UI + live SHAP |
| **Modular `src/` Package** | Reusable preprocessing & inference |
| **Target Encoding** | `addr_state` encoded from 2017 data |
| **Production Ready** | `Dockerfile`, `requirements.txt`, CI-ready |

---

## Project Structure

```bash
credit-risk-ai/
├── notebooks/              # Exploration (01_eda, 02_preprocess, 03_model)
├── src/                    # Production code
│   ├── preprocess.py       # Encoding + target encoding
│   ├── model.py            # Predict + SHAP
│   └── utils.py            # Helpers
├── api/main.py             # FastAPI server
├── dashboard/app.py        # Streamlit UI
├── data/
│   ├── processed.parquet   # 28 raw features
│   ├── train_encoded.parquet
│   └── test_encoded.parquet
├── models/
│   ├── xgb_model.pkl
│   └── shap_explainer.pkl
├── requirements.txt
├── Dockerfile
└── README.md
