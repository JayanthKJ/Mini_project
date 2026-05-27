import pandas as pd
import numpy as np
import os
import json
import joblib
import warnings
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


warnings.filterwarnings('ignore')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'AQ of adoloscents - Sheet.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'ml_models')

# Create ml_models directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

def run_training():
    print(" Starting Logistic Regression Baseline Training...\n")

  
    if not os.path.exists(DATA_PATH):
        print(f" ERROR: Dataset not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
   
    if 'Q1' not in df.columns:
        print("Renaming long column names to Q1-Q10...")
     
        question_cols = df.columns[0:9] 
        rename_map = {col: f'Q{i+1}' for i, col in enumerate(question_cols)}
        df = df.rename(columns=rename_map)

    
    if 'Target_Category' not in df.columns:
        print(" Engineering Target_Category from AQ scores...")
        def categorize_aq(score):
            if score < 2.5: return 0      
            elif score < 3.5: return 1    
            else: return 2                
        df['Target_Category'] = df['AQ'].apply(categorize_aq)

   
    features = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']
    X = df[features]
    y = df['Target_Category']

   
    print(" Splitting and Scaling data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_scaled_all = scaler.transform(X) 

    
    print(" Training Logistic Regression Model (Multi-Class)...")
    lr_model = LogisticRegression( solver='lbfgs', max_iter=1000, random_state=42)
    lr_model.fit(X_train_scaled, y_train)

    
    y_pred = lr_model.predict(X_test_scaled)
    y_proba = lr_model.predict_proba(X_test_scaled)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    
    try:
        auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
    except ValueError:
        auc = 0.0 

    print("🔄 Running 5-Fold Cross Validation...")
    cv_results = cross_validate(lr_model, X_scaled_all, y, cv=5, scoring=['accuracy'])
    cv_mean = cv_results['test_accuracy'].mean()
    cv_std = cv_results['test_accuracy'].std()

   
    print("💾 Saving Model, Scaler, and Metrics to /ml_models...")
    
    joblib.dump(lr_model, os.path.join(MODELS_DIR, 'logistic_regression_model.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    joblib.dump(X_train, os.path.join(MODELS_DIR, 'X_train.pkl')) # Saved for SHAP usage later

   
    metrics_file = os.path.join(MODELS_DIR, 'evaluation_metrics.json')
    metrics_data = []
    
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            try:
                metrics_data = json.load(f)
            except json.JSONDecodeError:
                pass 

    
    metrics_data = [m for m in metrics_data if m['model_name'] != 'Logistic Regression']

    # Append the new metrics
    metrics_data.append({
        'model_name': 'Logistic Regression',
        'accuracy': round(float(acc), 4),
        'f1_score': round(float(f1), 4),
        'auc_roc': round(float(auc), 4),
        'cv_mean': round(float(cv_mean), 4),
        'cv_std': round(float(cv_std), 4)
    })

    with open(metrics_file, 'w') as f:
        json.dump(metrics_data, f, indent=4)

    print("\n✅ SUCCESS: Baseline model is ready for deployment!")
    print("-" * 50)
    print(f"Accuracy : {acc:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"CV Mean  : {cv_mean:.4f} (± {cv_std:.4f})")
    print("-" * 50)
    print("You can now start your FastAPI server (`python main.py`).")

if __name__ == "__main__":
    run_training()