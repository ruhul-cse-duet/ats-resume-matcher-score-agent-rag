import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    # HuggingFace Configuration (REQUIRED)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", os.getenv("HF_TOKEN"))

    # HuggingFace Model Settings
    # Popular models you can use:
    # - "google/flan-t5-base" (Lightweight)
    # - "meta-llama/Llama-2-7b-chat-hf" (Requires approval)
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL")

    # Ollama Model Settings
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

    # Model Parameters
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))

    # File upload settings
    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ats.db")
    JWT_SECRET = os.getenv("JWT_SECRET", "ruhul_204085_amin")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "600"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


    @staticmethod
    def validate_config():
        """Validate configuration before running"""
        errors = []

        if not Config.HUGGINGFACE_API_KEY:
            errors.append("HUGGINGFACE_API_KEY or HF_TOKEN is required")
            errors.append("Get your token from: https://huggingface.co/settings/tokens")

        if not Config.HUGGINGFACE_MODEL:
            errors.append("HUGGINGFACE_MODEL must be specified")

        if not Config.OLLAMA_MODEL:
            errors.append("OLLAMA_MODEL must be specified")

        if not Config.EMBEDDING_MODEL:
            errors.append("EMBEDDING_MODEL must be specified")

        if errors:
            raise ValueError(
                "\n❌ Configuration Error:\n" +
                "\n".join(f"   • {e}" for e in errors) +
                "\n\nPlease update your .env file with required settings."
            )

        return True

# Create settings instance for backward compatibility
settings = Config

