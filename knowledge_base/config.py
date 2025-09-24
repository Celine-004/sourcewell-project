import os

# Weaviate connection configuration
WEAVIATE_HTTP_PORT = int(os.getenv("WEAVIATE_HTTP_PORT", "8080"))
WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))

# Calculator configuration (optional - consolidate constants)
SUPPORTED_CALCULATORS = ["FINDRISC", "ModifiedFramingham", "ColorectalScreening"]
REQUIRED_COLLECTIONS = ("MedicalGuideline", "ResearchAbstract")
MIN_GUIDELINES_REQUIRED = 5
