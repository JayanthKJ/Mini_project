from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import joblib
import os

# Import all routers
from router import predict, models, features, dimensions, health

# ═════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════════════════════
# MODEL REGISTRY (Global - Load models once at startup)
# ═════════════════════════════════════════════════════════════════════════════

class ModelRegistry:
    """Manage trained models and load them on startup"""
    
    def __init__(self, models_dir='ml_models'):
        """Initialize model registry"""
        self.models_dir = models_dir
        self.models = {}
        self.scaler = None
        self.shap_explainer = None
        self.X_train = None
        self.load_models()
    
    def load_models(self):
        """Load all trained models from disk"""
        try:
            logger.info(f"Loading models from {self.models_dir}/")
            
            # Check if directory exists
            if not os.path.exists(self.models_dir):
                logger.warning(f"Models directory '{self.models_dir}' not found!")
                return False
            
            # Load individual models
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
                    logger.info(f"✓ Loaded {model_name}")
                else:
                    logger.warning(f"✗ Model file not found: {path}")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("✓ Loaded scaler")
            else:
                logger.warning(f"Scaler not found: {scaler_path}")
            
            # Load SHAP explainer
            shap_path = os.path.join(self.models_dir, 'shap_explainer.pkl')
            if os.path.exists(shap_path):
                self.shap_explainer = joblib.load(shap_path)
                logger.info("✓ Loaded SHAP explainer")
            else:
                logger.warning(f"SHAP explainer not found: {shap_path}")
            
            # Load training data
            x_train_path = os.path.join(self.models_dir, 'X_train.pkl')
            if os.path.exists(x_train_path):
                self.X_train = joblib.load(x_train_path)
                logger.info("✓ Loaded training data for SHAP")
            else:
                logger.warning(f"Training data not found: {x_train_path}")
            
            if len(self.models) == 5:
                logger.info(f"✓ All models loaded successfully ({len(self.models)}/5)")
                return True
            else:
                logger.warning(f"⚠ Only {len(self.models)}/5 models loaded")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error loading models: {e}", exc_info=True)
            return False
    
    def predict(self, X, model_name):
        """Make prediction with specific model"""
        try:
            model = self.models[model_name]
            
            # Apply scaling for distance-based models
            if model_name in ['Logistic Regression', 'SVM']:
                X_processed = self.scaler.transform(X)
            else:
                X_processed = X
            
            prediction = model.predict(X_processed)
            proba = model.predict_proba(X_processed)
            
            return prediction[0], proba[0]
        except Exception as e:
            logger.error(f"Error predicting with {model_name}: {e}")
            raise

# ═════════════════════════════════════════════════════════════════════════════
# FASTAPI APP INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Adversity quotient of adoloscents",
    description="Exploring the impact of Adversity Quotient of Adoloscents Behavioural Pattern",
    
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")



@app.on_event("startup")
async def startup_event():
    """Initialize models when app starts"""
    global model_registry
    logger.info("="*70)
    logger.info("STARTING AQ PREDICTION SYSTEM")
    logger.info("="*70)
    
    model_registry = ModelRegistry()
    
    if len(model_registry.models) == 5:
        logger.info("✓ Application startup successful - All models loaded")
    else:
        logger.warning("⚠ Application startup with warnings - Some models missing")




logger.info("Registering routers...")

# Health check router
app.include_router(health.router)
logger.info("✓ Health router registered")

# Prediction router
app.include_router(predict.router)
logger.info("✓ Prediction router registered")

# Models comparison router
app.include_router(models.router)
logger.info("✓ Models router registered")

# Features router
app.include_router(features.router)
logger.info("✓ Features router registered")

# Dimensions router
app.include_router(dimensions.router)
logger.info("✓ Dimensions router registered")

logger.info("All routers registered successfully")



@app.get("/")
async def root():
    
    return {
        "message": "Exploring the Impact of Adversity Quotient in Adolescents’ Behavioural pattern",
        
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "redoc": "/redoc",
            "predict": "POST /predict",
            "models": "GET /model-comparison",
            "features": "GET /feature-importance",
            "dimensions": "GET /core-dimensions"
        
        }
    }



@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    logger.error(f"ValueError: {exc}")
    return {
        "error": "Validation Error",
        "message": str(exc)
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }

