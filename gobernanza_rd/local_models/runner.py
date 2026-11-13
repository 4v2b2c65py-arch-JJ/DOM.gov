# Local Model Runner - Supports Ollama, llama.cpp, vLLM
import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime

import aiohttp
import structlog

from config.settings import get_settings

settings = get_settings()
logger = structlog.get_logger()


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    VLLM = "vllm"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    LOCAL = "local"


@dataclass
class ModelConfig:
    provider: ModelProvider
    model_name: str
    role: str
    base_url: str
    api_key: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.1
    top_p: float = 0.9
    timeout: int = 120
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelResponse:
    content: str
    model: str
    provider: ModelProvider
    tokens_used: int = 0
    latency_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict] = None


class BaseModelRunner(ABC):
    """Abstract base class for model runners"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._total_latency = 0
        self._error_count = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        ...
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "role": self.config.role,
            "requests": self._request_count,
            "avg_latency_ms": self._total_latency / max(self._request_count, 1),
            "errors": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1)
        }


class OllamaRunner(BaseModelRunner):
    """Ollama local model runner"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        start = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": self.config.max_tokens,
                **self.config.extra_params
            }
        }
        
        async with self.session.post(
            f"{self.config.base_url}/api/chat",
            json=payload
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
        
        latency = int((time.time() - start) * 1000)
        self._request_count += 1
        self._total_latency += latency
        
        return ModelResponse(
            content=data["message"]["content"],
            model=self.config.model_name,
            provider=ModelProvider.OLLAMA,
            tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            latency_ms=latency,
            metadata={"eval_duration": data.get("eval_duration"), "prompt_eval_duration": data.get("prompt_eval_duration")},
            raw_response=data
        )
    
    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": self.config.max_tokens,
                **self.config.extra_params
            }
        }
        
        async with self.session.post(
            f"{self.config.base_url}/api/chat",
            json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                if line:
                    try:
                        data = json.loads(line.decode())
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def health_check(self) -> bool:
        try:
            async with self.session.get(f"{self.config.base_url}/api/tags") as resp:
                return resp.status == 200
        except Exception:
            return False
    
    async def list_models(self) -> List[str]:
        try:
            async with self.session.get(f"{self.config.base_url}/api/tags") as resp:
                resp.raise_for_status()
                data = await resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []
    
    async def pull_model(self, model_name: str) -> AsyncGenerator[Dict, None]:
        """Pull a model with progress"""
        async with self.session.post(
            f"{self.config.base_url}/api/pull",
            json={"name": model_name, "stream": True}
        ) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                if line:
                    try:
                        yield json.loads(line.decode())
                    except json.JSONDecodeError:
                        continue


class LlamaCppRunner(BaseModelRunner):
    """llama.cpp server runner (compatible with OpenAI API format)"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        start = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": False,
            **self.config.extra_params
        }
        
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        async with self.session.post(
            f"{self.config.base_url}/v1/chat/completions",
            json=payload,
            headers=headers
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
        
        latency = int((time.time() - start) * 1000)
        self._request_count += 1
        self._total_latency += latency
        
        choice = data["choices"][0]
        return ModelResponse(
            content=choice["message"]["content"],
            model=self.config.model_name,
            provider=ModelProvider.LLAMA_CPP,
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            latency_ms=latency,
            metadata={"finish_reason": choice.get("finish_reason")},
            raw_response=data
        )
    
    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True,
            **self.config.extra_params
        }
        
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        async with self.session.post(
            f"{self.config.base_url}/v1/chat/completions",
            json=payload,
            headers=headers
        ) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                line = line.decode().strip()
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if data["choices"][0]["delta"].get("content"):
                            yield data["choices"][0]["delta"]["content"]
                    except (json.JSONDecodeError, KeyError):
                        continue
    
    async def health_check(self) -> bool:
        try:
            async with self.session.get(f"{self.config.base_url}/v1/models") as resp:
                return resp.status == 200
        except Exception:
            return False


class VLLMRunner(BaseModelRunner):
    """vLLM runner (OpenAI API compatible)"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        # vLLM uses same API as llama.cpp
        return await LlamaCppRunner.generate(self, prompt, system_prompt, **kwargs)
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        return LlamaCppRunner.generate_stream(self, prompt, system_prompt, **kwargs)
    
    async def health_check(self) -> bool:
        return await LlamaCppRunner.health_check(self)


class ExternalModelRunner(BaseModelRunner):
    """Runner for external APIs (Anthropic, OpenAI, Google, Mistral, Cohere)"""
    
    PROVIDER_CONFIGS = {
        ModelProvider.ANTHROPIC: {
            "base_url": "https://api.anthropic.com/v1",
            "headers": lambda key: {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            "payload": lambda self, messages: {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                **self.config.extra_params
            },
            "extract": lambda data: (data["content"][0]["text"], data.get("usage", {}).get("output_tokens", 0) + data.get("usage", {}).get("input_tokens", 0))
        },
        ModelProvider.OPENAI: {
            "base_url": "https://api.openai.com/v1",
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "payload": lambda self, messages: {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                **self.config.extra_params
            },
            "extract": lambda data: (data["choices"][0]["message"]["content"], data.get("usage", {}).get("total_tokens", 0))
        },
        ModelProvider.GOOGLE: {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "headers": lambda key: {"Content-Type": "application/json"},
            "payload": lambda self, messages: {
                "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages],
                "generationConfig": {
                    "maxOutputTokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "topP": self.config.top_p,
                    **self.config.extra_params
                }
            },
            "extract": lambda data: (data["candidates"][0]["content"]["parts"][0]["text"], data.get("usageMetadata", {}).get("totalTokenCount", 0)),
            "url_suffix": lambda self: f"/models/{self.config.model_name}:generateContent?key={self.config.api_key}"
        },
        ModelProvider.MISTRAL: {
            "base_url": "https://api.mistral.ai/v1",
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "payload": lambda self, messages: {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                **self.config.extra_params
            },
            "extract": lambda data: (data["choices"][0]["message"]["content"], data.get("usage", {}).get("total_tokens", 0))
        },
        ModelProvider.COHERE: {
            "base_url": "https://api.cohere.ai/v1",
            "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            "payload": lambda self, messages: {
                "model": self.config.model_name,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "p": self.config.top_p,
                **self.config.extra_params
            },
            "extract": lambda data: (data["text"], data.get("meta", {}).get("tokens", {}).get("output_tokens", 0) + data.get("meta", {}).get("tokens", {}).get("input_tokens", 0))
        }
    }
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        start = time.time()
        
        provider_config = self.PROVIDER_CONFIGS[self.config.provider]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = provider_config["payload"](self, messages)
        headers = provider_config["headers"](self.config.api_key)
        
        url = provider_config["base_url"]
        if "url_suffix" in provider_config:
            url += provider_config["url_suffix"](self)
        else:
            url += "/chat/completions" if self.config.provider != ModelProvider.COHERE else "/chat"
        
        async with self.session.post(url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
        
        latency = int((time.time() - start) * 1000)
        self._request_count += 1
        self._total_latency += latency
        
        content, tokens = provider_config["extract"](data)
        
        return ModelResponse(
            content=content,
            model=self.config.model_name,
            provider=self.config.provider,
            tokens_used=tokens,
            latency_ms=latency,
            raw_response=data
        )
    
    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        # Simplified - would need provider-specific streaming implementations
        response = await self.generate(prompt, system_prompt, **kwargs)
        # Simulate streaming by yielding chunks
        words = response.content.split()
        for i in range(0, len(words), 5):
            yield " ".join(words[i:i+5]) + " "
            await asyncio.sleep(0.01)
    
    async def health_check(self) -> bool:
        provider_config = self.PROVIDER_CONFIGS[self.config.provider]
        try:
            # Simple test request
            await self.generate("test", max_tokens=1)
            return True
        except Exception:
            return False


def create_runner(config: ModelConfig) -> BaseModelRunner:
    """Factory function to create appropriate runner"""
    runners = {
        ModelProvider.OLLAMA: OllamaRunner,
        ModelProvider.LLAMA_CPP: LlamaCppRunner,
        ModelProvider.VLLM: VLLMRunner,
        ModelProvider.ANTHROPIC: ExternalModelRunner,
        ModelProvider.OPENAI: ExternalModelRunner,
        ModelProvider.GOOGLE: ExternalModelRunner,
        ModelProvider.MISTRAL: ExternalModelRunner,
        ModelProvider.COHERE: ExternalModelRunner,
    }
    
    runner_class: Any = runners.get(config.provider)
    if not runner_class:
        raise ValueError(f"No runner for provider: {config.provider}")
    
    return runner_class(config)


class ModelRunnerPool:
    """Pool of model runners for load balancing and failover"""
    
    def __init__(self):
        self.runners: Dict[str, BaseModelRunner] = {}
        self.primary: Dict[str, str] = {}  # role -> runner_id
        self.backups: Dict[str, List[str]] = {}  # role -> [runner_ids]
    
    async def add_runner(self, runner_id: str, config: ModelConfig, is_primary: bool = False):
        runner = create_runner(config)
        await runner.__aenter__()
        healthy = await runner.health_check()
        if not healthy:
            logger.warning(f"Runner {runner_id} health check failed", provider=config.provider, model=config.model_name)
        
        self.runners[runner_id] = runner
        
        if is_primary or config.role not in self.primary:
            self.primary[config.role] = runner_id
        else:
            if config.role not in self.backups:
                self.backups[config.role] = []
            self.backups[config.role].append(runner_id)

    async def close_all(self) -> None:
        for runner in self.runners.values():
            try:
                await runner.__aexit__(None, None, None)
            except Exception as exc:
                logger.warning("runner_close_failed", error=str(exc))
    
    async def get_runner(self, role: str) -> Optional[BaseModelRunner]:
        """Get best available runner for role"""
        # Try primary
        primary_id = self.primary.get(role)
        if primary_id and primary_id in self.runners:
            runner = self.runners[primary_id]
            if await runner.health_check():
                return runner
        
        # Try backups
        for backup_id in self.backups.get(role, []):
            if backup_id in self.runners:
                runner = self.runners[backup_id]
                if await runner.health_check():
                    logger.info(f"Using backup runner for {role}", primary=primary_id, backup=backup_id)
                    return runner
        
        return None
    
    async def generate_with_failover(self, role: str, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        """Generate with automatic failover"""
        runner = await self.get_runner(role)
        if not runner:
            raise RuntimeError(f"No healthy runner for role: {role}")
        
        try:
            return await runner.generate(prompt, system_prompt, **kwargs)
        except Exception as e:
            logger.error(f"Primary runner failed for {role}, trying backups", error=str(e))
            
            # Try backups
            for backup_id in self.backups.get(role, []):
                if backup_id in self.runners:
                    backup_runner = self.runners[backup_id]
                    if await backup_runner.health_check():
                        try:
                            return await backup_runner.generate(prompt, system_prompt, **kwargs)
                        except Exception:
                            continue
            
            raise RuntimeError(f"All runners failed for role: {role}")
    
    def get_all_stats(self) -> Dict[str, Any]:
        return {runner_id: runner.get_stats() for runner_id, runner in self.runners.items()}