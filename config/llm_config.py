"""
LLM Configuration Module
Configures DeepSeek (primary) and OpenRouter (secondary/free) providers
"""

import os
from typing import Dict, Any, Optional
from openai import OpenAI

class LLMConfig:
    """Configuration for LLM providers"""
    
    # DeepSeek Configuration (Primary)
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODELS = {
        "deepseek-chat": "deepseek-chat",  # Main model with tool calling support
        "deepseek-reasoner": "deepseek-reasoner",  # Reasoning model (NO tool calling - use only for complex reasoning)
        "deepseek-coder": "deepseek-coder",  # For code generation
    }
    
    # OpenRouter Configuration (Secondary - Free Models with Tool Calling)
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_FREE_MODELS = {
        # Latest FREE models with TOOL CALLING support (Updated Oct 2025)
        # ✅ = Supports tool/function calling
        
        # Google Gemini 2.0 (FREE, TOOLS ✅) - NEWEST & BEST
        "gemini-2.0-flash": "google/gemini-2.0-flash-exp:free",  # Latest, multimodal, 1M context, tools ✅
        "gemini-2.0-flash-thinking": "google/gemini-2.0-flash-thinking-exp:free",  # Reasoning mode, tools ✅
        "gemini-flash-1.5": "google/gemini-flash-1.5:free",  # Previous gen, stable, tools ✅
        "gemini-flash-1.5-8b": "google/gemini-flash-1.5-8b:free",  # Faster variant, tools ✅
        
        # Meta Llama 3.3 (FREE, TOOLS ✅) - Best Open Source
        "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct:free",  # Latest Llama, excellent, tools ✅
        "llama-3.1-405b": "meta-llama/llama-3.1-405b-instruct:free",  # Largest Llama, tools ✅
        "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct:free",  # Stable, tools ✅
        "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct:free",  # Fast, tools ✅
        
        # Qwen 3 (Alibaba) - Latest (FREE, TOOLS ✅)
        "qwen-3-235b": "qwen/qwen-3-235b-instruct:free",  # Newest, massive, tools ✅
        "qwen-2.5-72b": "qwen/qwen-2.5-72b-instruct:free",  # Previous gen, excellent, tools ✅
        "qwen-2.5-7b": "qwen/qwen-2.5-7b-instruct:free",  # Fast variant, tools ✅
        
        # Microsoft Phi-4 (FREE, TOOLS ✅) - Latest Small Model
        "phi-4": "microsoft/phi-4:free",  # Newest Phi, 14B params, tools ✅
        "phi-3.5-mini": "microsoft/phi-3.5-mini-128k-instruct:free",  # Updated Phi-3, tools ✅
        "phi-3-medium": "microsoft/phi-3-medium-128k-instruct:free",  # Stable, tools ✅
        
        # Mistral (FREE, TOOLS ✅)
        "mistral-7b": "mistralai/mistral-7b-instruct:free",  # Classic, reliable, tools ✅
        
        # DeepSeek via OpenRouter (FREE alternative)
        "deepseek-chat": "deepseek/deepseek-chat:free",  # If primary DeepSeek fails
    }
    
    # Model capabilities metadata
    MODEL_CAPABILITIES = {
        # DeepSeek
        "deepseek-chat": {"tools": True, "reasoning": False, "context": "128k", "version": "latest"},
        "deepseek-reasoner": {"tools": False, "reasoning": True, "context": "64k", "version": "latest"},
        "deepseek-coder": {"tools": True, "reasoning": False, "context": "128k", "version": "latest"},
        
        # Google Gemini 2.0 (Latest - Oct 2025)
        "gemini-2.0-flash": {"tools": True, "reasoning": True, "context": "1M", "multimodal": True, "version": "2.0"},
        "gemini-2.0-flash-thinking": {"tools": True, "reasoning": True, "context": "1M", "multimodal": True, "version": "2.0"},
        "gemini-flash-1.5": {"tools": True, "reasoning": True, "context": "1M", "multimodal": True, "version": "1.5"},
        "gemini-flash-1.5-8b": {"tools": True, "reasoning": False, "context": "1M", "multimodal": True, "version": "1.5"},
        
        # Meta Llama 3.x (Latest)
        "llama-3.3-70b": {"tools": True, "reasoning": True, "context": "128k", "version": "3.3"},
        "llama-3.1-405b": {"tools": True, "reasoning": True, "context": "128k", "version": "3.1"},
        "llama-3.1-70b": {"tools": True, "reasoning": True, "context": "128k", "version": "3.1"},
        "llama-3.1-8b": {"tools": True, "reasoning": False, "context": "128k", "version": "3.1"},
        
        # Qwen 3 (Latest - Oct 2025)
        "qwen-3-235b": {"tools": True, "reasoning": True, "context": "128k", "version": "3.0"},
        "qwen-2.5-72b": {"tools": True, "reasoning": True, "context": "128k", "version": "2.5"},
        "qwen-2.5-7b": {"tools": True, "reasoning": False, "context": "128k", "version": "2.5"},
        
        # Microsoft Phi-4 (Latest - Oct 2025)
        "phi-4": {"tools": True, "reasoning": True, "context": "128k", "version": "4.0"},
        "phi-3.5-mini": {"tools": True, "reasoning": True, "context": "128k", "version": "3.5"},
        "phi-3-medium": {"tools": True, "reasoning": True, "context": "128k", "version": "3.0"},
        
        # Mistral
        "mistral-7b": {"tools": True, "reasoning": False, "context": "32k", "version": "0.3"},
    }
    
    def __init__(self):
        """Initialize LLM configuration"""
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Initialize clients
        self.deepseek_client = None
        self.openrouter_client = None
        
        if self.deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.DEEPSEEK_BASE_URL
            )
        
        if self.openrouter_api_key:
            self.openrouter_client = OpenAI(
                api_key=self.openrouter_api_key,
                base_url=self.OPENROUTER_BASE_URL
            )
    
    def supports_tools(self, model: str) -> bool:
        """Check if a model supports tool/function calling
        
        Args:
            model: Model identifier
            
        Returns:
            True if model supports tools, False otherwise
        """
        capabilities = self.MODEL_CAPABILITIES.get(model, {})
        return capabilities.get("tools", False)
    
    def get_reasoning_model(self, provider: str = "deepseek") -> str:
        """Get the best reasoning model (no tools) for the provider
        
        Args:
            provider: 'deepseek' or 'openrouter'
            
        Returns:
            Model identifier for reasoning tasks
        """
        if provider == "deepseek":
            return "deepseek-reasoner"  # Dedicated reasoning model
        else:
            # For OpenRouter, use Gemini 2.0 Thinking or Qwen 3
            return "gemini-2.0-flash-thinking"  # Best free reasoning model
    
    def get_tool_model(self, provider: str = "deepseek") -> str:
        """Get the best model with tool calling support
        
        Args:
            provider: 'deepseek' or 'openrouter'
            
        Returns:
            Model identifier that supports tools
        """
        if provider == "deepseek":
            return "deepseek-chat"  # Main model with tools
        else:
            # Best free models with tools: Gemini 2.0 > Qwen 3 > Llama 3.3
            return "gemini-2.0-flash"  # Latest and best free model
    
    def get_client(self, provider: str = "deepseek") -> Optional[OpenAI]:
        """Get LLM client for specified provider
        
        Args:
            provider: 'deepseek' or 'openrouter'
            
        Returns:
            OpenAI client or None
        """
        if provider == "deepseek":
            return self.deepseek_client
        elif provider == "openrouter":
            return self.openrouter_client
        return None
    
    def call_llm(
        self, 
        prompt: str, 
        system_message: str = "You are a professional portfolio analyst.",
        model: str = "deepseek-chat",
        provider: str = "deepseek",
        temperature: float = 0.3,
        max_tokens: int = 1500,
        use_tools: bool = False,
        auto_select_model: bool = True
    ) -> str:
        """Call LLM with automatic fallback and model selection
        
        Args:
            prompt: User prompt
            system_message: System message
            model: Model identifier (auto-selected if use_tools=True)
            provider: 'deepseek' or 'openrouter'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_tools: If True, ensure model supports tool calling
            auto_select_model: If True, auto-select appropriate model based on use_tools
            
        Returns:
            LLM response text
        """
        # Auto-select model based on tool requirement
        if auto_select_model:
            if use_tools:
                model = self.get_tool_model(provider)
                print(f"🔧 Auto-selected tool-capable model: {model}")
            elif "reason" in model.lower() or model == "deepseek-reasoner":
                # Keep reasoning model selection
                if provider == "deepseek" and model != "deepseek-reasoner":
                    model = "deepseek-reasoner"
                print(f"🧠 Using reasoning model: {model}")
        
        # Warn if using tools with non-tool model
        if use_tools and not self.supports_tools(model):
            print(f"⚠️ Warning: {model} doesn't support tools. Switching to {self.get_tool_model(provider)}")
            model = self.get_tool_model(provider)
        
        # Try primary provider (DeepSeek)
        if provider == "deepseek" and self.deepseek_client:
            try:
                model_id = self.DEEPSEEK_MODELS.get(model, "deepseek-chat")
                response = self.deepseek_client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                return content if content else ""
            except Exception as e:
                print(f"⚠️ DeepSeek error: {e}")
                print("🔄 Falling back to OpenRouter...")
                provider = "openrouter"
        
        # Try secondary provider (OpenRouter - Free models)
        if provider == "openrouter" and self.openrouter_client:
            try:
                # Use free model
                free_model = self.OPENROUTER_FREE_MODELS.get(model, "meta-llama/llama-3.1-8b-instruct:free")
                
                response = self.openrouter_client.chat.completions.create(
                    model=free_model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                return content if content else ""
            except Exception as e:
                print(f"❌ OpenRouter error: {e}")
                return f'{{"error": "Both providers failed: {e}"}}'
        
        # No provider available
        if not self.deepseek_client and not self.openrouter_client:
            return '{"error": "No API keys configured. Set DEEPSEEK_API_KEY or OPENROUTER_API_KEY"}'
        
        return '{"error": "Unknown error occurred"}'
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get available models from all providers
        
        Returns:
            Dictionary of available models by provider
        """
        available = {
            "deepseek": {
                "available": self.deepseek_client is not None,
                "models": list(self.DEEPSEEK_MODELS.keys()) if self.deepseek_client else []
            },
            "openrouter": {
                "available": self.openrouter_client is not None,
                "models": list(self.OPENROUTER_FREE_MODELS.keys()) if self.openrouter_client else []
            }
        }
        return available


# Global instance
llm_config = LLMConfig()


def get_llm_response(
    prompt: str,
    system_message: str = "You are a professional portfolio analyst.",
    model: str = "deepseek-chat",
    provider: str = "deepseek",
    **kwargs
) -> str:
    """Convenience function to get LLM response
    
    Args:
        prompt: User prompt
        system_message: System message
        model: Model to use
        provider: Provider to use ('deepseek' or 'openrouter')
        **kwargs: Additional arguments for call_llm
        
    Returns:
        LLM response text
    """
    return llm_config.call_llm(
        prompt=prompt,
        system_message=system_message,
        model=model,
        provider=provider,
        **kwargs
    )


if __name__ == "__main__":
    """Test LLM configuration"""
    print("🔧 Testing LLM Configuration\n")
    
    # Check available models
    available = llm_config.get_available_models()
    print("📊 Available Models:")
    for provider, info in available.items():
        status = "✅ Connected" if info["available"] else "❌ Not configured"
        print(f"\n{provider.upper()}: {status}")
        if info["models"]:
            for model in info["models"]:
                print(f"  • {model}")
    
    # Test call if any provider is available
    if llm_config.deepseek_client or llm_config.openrouter_client:
        print("\n🧪 Testing LLM call...")
        test_prompt = "Say 'Hello from AI trading system!' in one sentence."
        
        # Try DeepSeek first
        if llm_config.deepseek_client:
            print("\n🤖 Testing DeepSeek:")
            response = get_llm_response(test_prompt, provider="deepseek")
            print(f"Response: {response}")
        
        # Try OpenRouter
        if llm_config.openrouter_client:
            print("\n🌐 Testing OpenRouter (free model):")
            response = get_llm_response(test_prompt, provider="openrouter", model="llama-3.1-8b")
            print(f"Response: {response}")
    else:
        print("\n⚠️ No API keys configured. Set environment variables:")
        print("  export DEEPSEEK_API_KEY='your-key'")
        print("  export OPENROUTER_API_KEY='your-key'")
