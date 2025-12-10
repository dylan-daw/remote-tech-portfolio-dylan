# Project 1 – Titanic Survival Analysis

This project uses the classic Kaggle Titanic dataset to explore which
passenger features are most predictive of survival.

The goal is **not** to build the world’s best model, but to show that I
can:

- Work with CSV data in pandas
- Clean and preprocess messy real-world data
- Do basic exploratory data analysis (EDA) with plots
- Train and evaluate a simple model
- Explain results in clear, non-jargony language

---

## Project Plan

The accompanying notebook `titanic_analysis.ipynb` will be organized into:

1. **Load data**  
   - Read the Titanic CSV into pandas  
   - Quick look at columns, missing values, and basic stats

2. **Clean & preprocess**  
   - Handle missing values (e.g. age, cabin)  
   - Encode categorical variables (sex, embarkation, etc.)  
   - Create a few simple engineered features

3. **Exploratory Data Analysis (EDA)**  
   - Plot survival rate by sex, passenger class, and age range  
   - Look at correlations and simple pivot tables

4. **Baseline model**  
   - Train a basic model (e.g. logistic regression or random forest)  
   - Split into train/validation set  
   - Show accuracy and a couple of simple metrics

5. **Results & next steps**  
   - Briefly explain what seems to matter most for survival  
   - List possible improvements (tuning, better features, etc.)

---

## Status

- Notebook created: `titanic_analysis.ipynb`  
- Next step: implement “Load data” and “Clean & preprocess” sections.
