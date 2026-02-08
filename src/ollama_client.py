"""
Ollama API client for Mitch Discord Bot.

Provides async HTTP interface to local Ollama instance.
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for communicating with local Ollama API."""
    
    def __init__(self, host: str = "http://localhost:11434", 
                 model: str = "phi3:mini",
                 timeout: int = 60,
                 temperature: float = 0.8,
                 max_tokens: int = 300):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama API endpoint (default: http://localhost:11434)
            model: Model name to use (default: phi3:mini)
            timeout: Request timeout in seconds (default: 60)
            temperature: Sampling temperature 0.0-1.0 (default: 0.8)
            max_tokens: Maximum tokens to generate (default: 300)
        """
        self.host = host.rstrip('/')  # Remove trailing slash if present
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.endpoint = f"{self.host}/api/generate"
        
        logger.info(f"Ollama client initialized: {self.host}, model={self.model}")
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text completion from Ollama.
        
        Args:
            prompt: The prompt text to send to the model
            
        Returns:
            Generated text response
            
        Raises:
            aiohttp.ClientConnectionError: If Ollama is not running
            asyncio.TimeoutError: If request exceeds timeout
            Exception: For other API errors
        """
        request_body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        logger.debug(f"Sending request to Ollama: {len(prompt)} chars")
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json=request_body,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
                    
                    data = await response.json()
                    generated_text = data.get("response", "")
                    
                    elapsed = asyncio.get_event_loop().time() - start_time
                    logger.info(f"Ollama response received ({elapsed:.1f}s, {len(generated_text)} chars)")
                    
                    return generated_text
                    
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {self.host}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is running and responsive.
        
        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.host,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
