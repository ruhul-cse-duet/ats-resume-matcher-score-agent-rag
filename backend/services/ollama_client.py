import requests
import logging
import time
from backend.app.config import settings

logger = logging.getLogger(__name__)

def call_ollama(prompt: str, model: str = None, timeout: int = None, max_retries: int = 3) -> str:
    """
    Call Ollama API with comprehensive error handling and retry logic
    
    Args:
        prompt: The input text prompt
        model: Ollama model name (default from settings)
        timeout: Request timeout in seconds (default from settings)
        max_retries: Maximum number of retry attempts for timeouts (default: 3)
    
    Returns:
        str: LLM response text
    """
    model = settings.OLLAMA_MODEL
    timeout = settings.OLLAMA_TIMEOUT
    
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_predict": 400
        }
    }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Ollama (attempt {attempt + 1}/{max_retries}) with model: {model}")
            
            resp = requests.post(
                settings.OLLAMA_URL,
                json=payload, 
                timeout=timeout
            )
            resp.raise_for_status()
            
            data = resp.json()
            response_text = data.get("response", "")
            
            if not response_text:
                logger.warning("Ollama returned empty response")
                raise ValueError("Empty response from LLM")
            
            logger.info(f"Successfully received response from Ollama")
            return response_text
            
        except requests.exceptions.Timeout as e:
            last_error = e
            logger.warning(f"Ollama request timeout (attempt {attempt + 1}/{max_retries})")
            
            # If model is loading first time, wait a bit and retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Waiting {wait_time}s before retry (model may be loading)...")
                time.sleep(wait_time)
                continue
            
            logger.error(f"Ollama request timeout after {max_retries} attempts")
            raise TimeoutError(
                f"LLM request timed out after {max_retries} attempts. "
                f"Model '{model}' may be too large or system resources limited. "
                f"Try a smaller model like 'gemma2:2b' or increase OLLAMA_TIMEOUT."
            )
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {settings.OLLAMA_URL}")
            raise ConnectionError(
                f"Cannot connect to LLM service at {settings.OLLAMA_URL}. "
                f"Please ensure Ollama is running with: ollama serve"
            )
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Ollama: {e}")
            
            if e.response.status_code == 404:
                raise ValueError(
                    f"Model '{model}' not found. "
                    f"Please pull the model first: ollama pull {model}"
                )
            elif e.response.status_code == 500:
                # Internal server error - often means model is corrupted or incompatible
                raise ValueError(
                    f"Ollama internal error with model '{model}'. "
                    f"Try: 1) Restart Ollama, 2) Re-pull model: ollama pull {model}"
                )
            else:
                raise ValueError(f"LLM service error: HTTP {e.response.status_code}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise ConnectionError(f"Error communicating with LLM service: {str(e)}")
        
        except ValueError as e:
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {str(e)}")
            raise RuntimeError(f"Unexpected error with LLM service: {str(e)}")
    
    # If all retries failed
    if last_error:
        raise TimeoutError(
            f"Failed after {max_retries} attempts. Last error: {str(last_error)}"
        )
