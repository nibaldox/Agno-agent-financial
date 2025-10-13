# 🤖 OpenRouter API Key Setup

## Overview
The Agente Agno v3.8.0 includes AI-powered insights using **DeepSeek** via OpenRouter. This provides natural language analysis of your trading performance at a very low cost (~$0.14 per 1M tokens).

## Why OpenRouter + DeepSeek?
- **Cost-effective**: ~100x cheaper than GPT-4
- **Quality**: DeepSeek-V3 provides excellent financial analysis
- **Unified API**: Access multiple AI models through one interface
- **Pay-as-you-go**: No subscriptions, only pay for what you use

## Setup Steps

### 1. Get Your API Key

1. Visit: https://openrouter.ai/
2. Sign up or log in
3. Go to: https://openrouter.ai/keys
4. Click **"Create Key"**
5. Copy your API key (starts with `sk-or-v1-...`)

### 2. Set Environment Variable

#### Windows PowerShell (Current Session)
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

#### Windows PowerShell (Permanent)
```powershell
[System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'sk-or-v1-your-key-here', 'User')
```

#### Windows CMD
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

#### Linux/Mac
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

For permanent setup, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export OPENROUTER_API_KEY="sk-or-v1-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify Setup

```powershell
# Check if variable is set
echo $env:OPENROUTER_API_KEY

# Should output: sk-or-v1-...
```

### 4. Run with AI Insights

```powershell
# Generate report with AI insights
python agente-agno/fase2_example_interactive.py --data-dir "Scripts and CSV Files"

# You should see:
# [STEP 4.5] Generating AI insights...
#   ✅ AI insights generated (1,234 tokens)
```

## Cost Estimate

**DeepSeek Pricing** (via OpenRouter):
- Input: ~$0.14 per 1M tokens
- Output: ~$0.28 per 1M tokens

**Typical Report**:
- Input: ~1,000 tokens (portfolio data + metrics)
- Output: ~1,500 tokens (analysis + recommendations)
- **Cost per report: ~$0.0005 (less than 1 cent!)**

Even with 1,000 reports, you'd spend less than $1.

## What You Get

The AI insights section includes:

1. **📋 Executive Summary** - High-level portfolio overview
2. **📊 Performance Analysis** - Deep dive into returns and metrics
3. **⚠️ Risk Assessment** - Analysis of drawdown, volatility, concentration
4. **💡 Recommendations** - Actionable suggestions for improvement
5. **✅ Key Strengths** - What's working well
6. **🔧 Areas for Improvement** - What needs attention

All analysis is in **Spanish** and tailored to your actual portfolio data.

## Troubleshooting

### "Skipping AI insights: OPENROUTER_API_KEY not set"
- Environment variable not found
- Solution: Follow Step 2 above and restart your terminal

### "Skipping AI insights: LLM insights not available"
- Module import failed
- Solution: Ensure `core/llm_insights.py` exists

### "API returned error 401"
- Invalid API key
- Solution: Check your key at https://openrouter.ai/keys

### "API returned error 429"
- Rate limit exceeded (rare with DeepSeek)
- Solution: Wait a few seconds and retry

### High costs?
- DeepSeek is extremely cheap (~$0.0005 per report)
- Check usage at: https://openrouter.ai/activity
- Consider using `quick_summary()` method for even lower costs

## Optional: Use Different Model

Edit `core/llm_insights.py` to use a different model:

```python
# Current (DeepSeek - cheapest)
llm_gen = LLMInsightsGenerator(model="deepseek/deepseek-chat")

# Alternative: GPT-4o-mini (more expensive but still cheap)
llm_gen = LLMInsightsGenerator(model="openai/gpt-4o-mini")

# Alternative: Claude (most expensive)
llm_gen = LLMInsightsGenerator(model="anthropic/claude-3-haiku")
```

See all models: https://openrouter.ai/models

## Running Without AI Insights

If you don't want to use AI insights, simply:
1. Don't set the `OPENROUTER_API_KEY` variable
2. The system will skip insights generation gracefully
3. Report will still include all charts and metrics

## Questions?

- OpenRouter Docs: https://openrouter.ai/docs
- DeepSeek Info: https://openrouter.ai/models/deepseek/deepseek-chat
- Issues: Check the console output for detailed error messages

---

**Cost Reminder**: With DeepSeek, even 10,000 reports costs less than $5. It's extremely cost-effective! 🎉
