from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import joblib
import json
import os

from router import predict, models, features, dimensions, health

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelRegistry:
    """Manage trained models and dynamic ML metadata"""
    
    def __init__(self, models_dir='ml_models'):
        self.models_dir = models_dir
        self.models = {}
        self.scaler = None
        self.shap_explainer = None
        self.X_train = None
        
        # New dynamic metadata storage
        self.evaluation_metrics = []
        self.global_feature_importance = []
        
        self.load_models()
    
    def load_models(self):
        try:
            if not os.path.exists(self.models_dir):
                logger.warning(f"Models directory '{self.models_dir}' not found!")
                return False
            
            # 1. Load ML Models
            model_files = {
                'Logistic Regression': 'logistic_regression_model.pkl',
                'Decision Tree': 'decision_tree_model.pkl',
                'Random Forest': 'random_forest_model.pkl',
                'SVM': 'svm_model.pkl',
                'XGBoost': 'xgb_model.pkl'
            }
            for model_name, filename in model_files.items():
                path = os.path.join(self.models_dir, filename)
                if os.path.exists(path):
                    self.models[model_name] = joblib.load(path)
            
            # 2. Load ML Components
            if os.path.exists(os.path.join(self.models_dir, 'scaler.pkl')):
                self.scaler = joblib.load(os.path.join(self.models_dir, 'scaler.pkl'))
            if os.path.exists(os.path.join(self.models_dir, 'shap_explainer.pkl')):
                self.shap_explainer = joblib.load(os.path.join(self.models_dir, 'shap_explainer.pkl'))
            if os.path.exists(os.path.join(self.models_dir, 'X_train.pkl')):
                self.X_train = joblib.load(os.path.join(self.models_dir, 'X_train.pkl'))

            # 3. LOAD DYNAMIC JSON METADATA (No Hardcoding!)
            metrics_path = os.path.join(self.models_dir, 'evaluation_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.evaluation_metrics = json.load(f)

            features_path = os.path.join(self.models_dir, 'feature_importance.json')
            if os.path.exists(features_path):
                with open(features_path, 'r') as f:
                    self.global_feature_importance = json.load(f)

            logger.info("Dynamic ML assets loaded successfully.")
            return True
                
        except Exception as e:
            logger.error(f"Error loading models: {e}", exc_info=True)
            return False
    
    def predict(self, X, model_name):
        model = self.models[model_name]
        X_processed = self.scaler.transform(X) if model_name in ['Logistic Regression', 'SVM'] else X
        return model.predict(X_processed)[0], model.predict_proba(X_processed)[0]

app = FastAPI(title="Exploring the Adversity quotient of adoloscents a behavioural pattern")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global model_registry
    model_registry = ModelRegistry()

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(models.router)
app.include_router(features.router)
app.include_router(dimensions.router)

@app.get("/")
async def root():
    return {"AQ of adoloscents"}