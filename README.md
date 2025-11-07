# Financial Analyst Bot 🤖💰

An automated Bitcoin trading analysis pipeline using CrewAI, OpenAI GPT-4o, and SerpAPI. This bot searches for recent Bitcoin articles, analyzes them, and provides buy/sell/hold recommendations via email.

## Features

- 🔍 **Google Search Agent**: Uses SerpAPI to find the top 10 most recent Bitcoin articles
- 📰 **Article Reader Agent**: Extracts key information and creates summaries
- 🧠 **Synthesis Agent**: Combines summaries into a coherent market overview
- 💼 **Analyst Agent**: Provides clear BUY/SELL/HOLD recommendations
- 🎨 **Web Designer Agent**: Creates stunning black and pink themed HTML reports
- 📧 **Email Automation**: Sends daily reports via Gmail
- ⏰ **Scheduled Runs**: Automatically runs daily at 8 AM

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/financial_analyst_bot.git
   cd financial_analyst_bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   GMAIL_ADDRESS=your_email@gmail.com
   GMAIL_PASSWORD=your_gmail_app_password
   ```

   **Note:** If you have 2FA enabled on Gmail, you'll need to use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password.

## Usage

### Run Once
```bash
python run_and_email.py
```

### Run with Scheduler (Daily at 8 AM)
```bash
python scheduled_email.py
```

This will:
1. Run the analysis and send email immediately
2. Schedule daily runs at 8:00 AM
3. Keep running until you stop it (Ctrl+C)

## How It Works

1. **Search**: Finds the top 10 most recent Bitcoin articles from the past 24 hours
2. **Analyze**: Extracts key information including price movements, sentiment, and trading signals
3. **Synthesize**: Combines all insights into a coherent market overview
4. **Recommend**: Provides a clear BUY/SELL/HOLD recommendation with reasoning
5. **Design**: Creates a beautiful HTML report with Gen Z styling
6. **Email**: Sends the report to the configured email address

## Output

The bot provides:
- Overall market sentiment (bullish/bearish/neutral)
- Key trends and patterns
- Trading recommendation (BUY/SELL/HOLD)
- Confidence level
- Risk factors
- Actionable advice for today's trading
- Beautiful HTML report with all analysis

## Requirements

- Python 3.10+
- OpenAI API key (for GPT-4o)
- SerpAPI key (for Google News search)
- Gmail account (for sending emails)

## Project Structure

```
financial_analyst_bot/
├── bitcoin_analyzer.py      # Main analysis workflow with CrewAI agents
├── run_and_email.py         # Runs analysis and sends email
├── scheduled_email.py       # Scheduler for daily runs
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .env                    # Environment variables (not in repo)
```

## License

MIT License
