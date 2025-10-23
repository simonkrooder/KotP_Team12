import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables from /src/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

PROJECT_ENDPOINT = os.getenv('PROJECT_ENDPOINT')
MODEL_DEPLOYMENT = os.getenv('AGENT_MODEL_DEPLOYMENT_NAME')

def get_project_client():
    """
    Returns an initialized AIProjectClient using credentials from .env
    """
    return AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

def get_model_deployment():
    """
    Returns the model deployment name from .env
    """
    return MODEL_DEPLOYMENT