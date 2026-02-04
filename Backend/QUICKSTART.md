# 🚀 Quick Start Guide - Groq API Setup

## Step 1: Get Your Groq API Key

1. Go to **https://console.groq.com/keys**
2. Sign in or create an account (free!)
3. Click "Create API Key"
4. Copy your API key (starts with `gsk_`)

## Step 2: Update Your .env File

Open `Backend/.env` and replace this line:

```env
XAI_API_KEY=your_groq_api_key_here
```

With your actual Groq API key:

```env
XAI_API_KEY=gsk_your_actual_key_here
```

## Step 3: Run the Example

```bash
cd Backend
python example_usage.py
```

## What You'll See

The system will:
- ✅ Auto-detect your Groq API key
- 🚀 Use Groq's ultra-fast Llama 3.3 70B model
- 🧠 Run the complete agentic reasoning cycle
- 💡 Generate creative writing suggestions

## Why Groq?

- **Ultra-fast inference** - Responses in seconds
- **Generous free tier** - Great for development
- **Powerful models** - Llama 3.3 70B is excellent for creative reasoning
- **OpenAI-compatible API** - Easy integration

## Troubleshooting

**If you see authentication errors:**
- Make sure your API key starts with `gsk_`
- Check that there are no extra spaces in the `.env` file
- Verify your key is active at https://console.groq.com/keys

**If you want to test without API:**
- The example already includes a mock mode
- Just run `python example_usage.py` and it will work with mock data

## Next Steps

Once working:
1. Integrate with other NOLAN modules (NLP, Knowledge Graph, etc.)
2. Add API endpoints for frontend
3. Connect to MongoDB for persistence
4. Implement preference learning system

Enjoy building with NOLAN! 🎉
