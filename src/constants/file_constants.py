import os
PRODUCTION_MODEL_FILE_PATH = os.path.join("production_model")
INTERACTIONS_MODEL_FILE_PATH = "production_interactions_model.pkl"
COURSES_MODEL_FILE_PATH = "production_courses_model.pkl"
INTERACTIONS_MATRIX_FILE_PATH = "production_interaction_matrix.npz"

FEATURE_STORE_FILE_PATH = os.getenv("FEAST_FEATURE_STORE_REPO_PATH")