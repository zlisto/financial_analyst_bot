"""
Bitcoin Trading Analysis App using CrewAI
Analyzes recent Bitcoin articles and provides buy/sell recommendations
"""

import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding issues (only if not already wrapped)
if sys.platform == 'win32':
    try:
        import io
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not isinstance(sys.stdout, io.TextIOWrapper):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not isinstance(sys.stderr, io.TextIOWrapper):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass  # Ignore if already wrapped, closed, or can't be wrapped
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import FileWriterTool
from langchain_core.tools import tool
from datetime import datetime
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

# Check if API keys are set
openai_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_API_KEY")

if not openai_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please add it.")
if not serpapi_key:
    raise ValueError("SERPAPI_API_KEY not found in .env file. Please add it.")

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)


# Custom SerpAPI tool to avoid interactive prompts
@tool("search_bitcoin_articles")
def search_bitcoin_articles(query: str = "Bitcoin BTC market price trading news today") -> str:
    """Search Google News for recent Bitcoin articles from the past 24 hours.
    
    Args:
        query: Search query string (default: Bitcoin BTC market price trading news today)
    
    Returns:
        Formatted string with article titles, sources, dates, and snippets
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY not found in environment variables"
        
        # Use default query if empty or just whitespace
        if not query or not query.strip():
            query = "Bitcoin BTC market price trading news today"
        
        params = {
            "q": query.strip(),
            "api_key": api_key,
            "num": 10,
            "tbm": "nws",  # News search
            "tbs": "qdr:d"  # Past day (recent articles)
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for API errors
        if "error" in results:
            return f"SerpAPI Error: {results.get('error', 'Unknown error')}"
        
        articles = []
        if "news_results" in results and results["news_results"]:
            for item in results["news_results"][:10]:
                article_text = f"Title: {item.get('title', 'N/A')}\n"
                article_text += f"Source: {item.get('source', 'N/A')}\n"
                article_text += f"Date: {item.get('date', 'N/A')}\n"
                article_text += f"Snippet: {item.get('snippet', 'N/A')}\n"
                if "link" in item:
                    article_text += f"Link: {item['link']}\n"
                article_text += "\n---\n"
                articles.append(article_text)
        
        if not articles:
            return "No recent articles found. Try adjusting the search query or check if there are any articles from the past 24 hours."
        
        return "\n".join(articles)
    except KeyError as e:
        return f"Error: Missing expected data in API response - {str(e)}"
    except Exception as e:
        return f"Error searching: {str(e)}"

# Initialize tools
write_html_file = FileWriterTool(file_path="output.html")


# Define Agents
google_search_agent = Agent(
    role="Google Search Specialist",
    goal="Find the most recent and relevant Bitcoin articles from the past 24 hours",
    backstory="""You are an expert at finding the latest news and articles about Bitcoin.
    You use Google News search to find the top 10 most recent and relevant articles
    about Bitcoin market trends, price movements, and trading signals.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_bitcoin_articles],
    llm=llm
)

article_reader_agent = Agent(
    role="Article Analyst",
    goal="Extract key information and create concise summaries from Bitcoin articles",
    backstory="""You are a financial news analyst specializing in cryptocurrency markets.
    You read articles carefully and extract the most important information including:
    - Price movements and trends
    - Market sentiment (bullish/bearish)
    - Key events or news
    - Trading signals and indicators
    - Expert opinions and predictions""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

synthesis_agent = Agent(
    role="Market Synthesis Expert",
    goal="Combine all article summaries into a coherent market overview",
    backstory="""You are a senior market analyst who synthesizes information from multiple sources.
    You identify patterns, trends, and consensus views across different articles.
    You highlight conflicting information and key insights that emerge from the collective analysis.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

analyst_agent = Agent(
    role="Trading Analyst",
    goal="Provide clear buy/sell/hold recommendations based on market analysis",
    backstory="""You are an experienced cryptocurrency trading analyst with a track record
    of making profitable recommendations. You analyze market sentiment, trends, and news
    to provide actionable trading advice. You consider risk factors and provide clear,
    confident recommendations for today's trading action.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

webpage_agent = Agent(
    role="Gen Z Web Designer",
    goal="Create a stunning black and pink themed HTML webpage with all the Bitcoin analysis in a fun, Gen Z tone",
    backstory="""You're a Gen Z web designer who's absolutely obsessed with creating fire websites.
    You speak in Gen Z slang, use emojis, and make everything look absolutely stunning.
    You love black and pink color schemes, modern gradients, and making financial data look cool.
    You're funny, relatable, and know how to make boring financial stuff actually interesting.
    You create websites that make people go 'no cap, this is actually sick'.""",
    verbose=True,
    allow_delegation=False,
    tools=[write_html_file],
    llm=llm
)


# Define Tasks
search_task = Task(
    description="""Search for the top 10 most recent Bitcoin articles from the past 24 hours.
    Use the search tool to search for: "Bitcoin BTC market price trading news today"
    Focus on finding articles about:
    - Bitcoin price movements
    - Market trends and analysis
    - Trading signals
    - Major news affecting Bitcoin
    
    Return the formatted list of articles with titles, sources, dates, and snippets.""",
    agent=google_search_agent,
    expected_output="A formatted list of recent Bitcoin articles with titles, sources, dates, and snippets"
)

read_task = Task(
    description="""Read and analyze each article found by the search agent.
    Use the context from the previous task (search results).
    For each article, extract:
    1. Key price information and movements
    2. Market sentiment (bullish, bearish, neutral)
    3. Important events or news
    4. Trading signals or indicators mentioned
    5. Expert opinions or predictions
    
    Create a concise summary for each article (2-3 sentences per article).
    Combine all summaries into a single document.""",
    agent=article_reader_agent,
    context=[search_task],
    expected_output="A comprehensive summary document with key insights from all articles, including market sentiment and price trends"
)

synthesis_task = Task(
    description="""Synthesize all the article summaries into a single coherent market overview.
    Use the context from the article reader agent's summaries.
    Identify:
    - Overall market sentiment (bullish/bearish/neutral)
    - Key trends and patterns across articles
    - Consensus views vs. conflicting opinions
    - Most important factors affecting Bitcoin today
    - Risk factors and concerns mentioned
    
    Create a clear, structured synthesis that highlights the most critical insights.""",
    agent=synthesis_agent,
    context=[read_task],
    expected_output="A synthesized market overview highlighting key insights, trends, and patterns from all articles"
)

analysis_task = Task(
    description="""Based on the synthesized market overview, provide a clear trading recommendation.
    Use the context from the synthesis agent's market overview.
    Analyze:
    - Overall market sentiment
    - Price trends and momentum
    - Risk factors
    - Key events or news impact
    
    Provide a clear recommendation: BUY, SELL, or HOLD
    Include:
    - Your recommendation (BUY/SELL/HOLD)
    - Confidence level (High/Medium/Low)
    - Key reasons for the recommendation
    - Important risk factors to consider
    - Suggested action for today's trading
    
    Be decisive and actionable.""",
    agent=analyst_agent,
    context=[synthesis_task],
    expected_output="A clear trading recommendation (BUY/SELL/HOLD) with reasoning, confidence level, and actionable advice for today"
)

webpage_task = Task(
    description="""Create a stunning HTML webpage (output.html) with a black and pink theme that includes:
    
    1. All the article titles/names from the search results
    2. The article analysis/summaries from the article reader
    3. The market synthesis overview
    4. The final trading recommendation (BUY/SELL/HOLD)
    
    Use context from ALL previous tasks: search_task, read_task, synthesis_task, and analysis_task.
    
    Style requirements:
    - Black background with pink accents (#FF1493, #FF69B4, hot pink colors)
    - Modern, Gen Z aesthetic with gradients
    - Use Gen Z slang and funny, relatable language
    - Make it visually stunning with smooth animations
    - Include emojis and make it engaging
    - Use modern CSS (gradients, shadows, hover effects)
    - Make the recommendation stand out prominently
    - Include the current date/time
    
    Write in a Gen Z tone - be funny, use slang like "no cap", "fr fr", "that's fire", "slaps", etc.
    Make it feel like a cool crypto trading dashboard that your friends would actually want to use.
    
    IMPORTANT: Generate the complete HTML code as a string. The HTML will be saved to output.html.
    Make sure all HTML is properly formatted and complete with <!DOCTYPE html>, <html>, <head>, and <body> tags.
    Use the write_html_file tool to save the complete HTML string to output.html.""",
    agent=webpage_agent,
    context=[search_task, read_task, synthesis_task, analysis_task],
    expected_output="A complete, styled HTML file saved to output.html with all analysis data in a black and pink Gen Z themed design"
)


def run_bitcoin_analysis():
    """Main function to run the Bitcoin analysis workflow"""
    print("Starting Bitcoin Trading Analysis...")
    print("="*80 + "\n")
    
    # Create and run the crew
    crew = Crew(
        agents=[google_search_agent, article_reader_agent, synthesis_agent, analyst_agent, webpage_agent],
        tasks=[search_task, read_task, synthesis_task, analysis_task, webpage_task],
        process=Process.sequential,
        verbose=True
    )
    
    print("CrewAI agents are working...\n")
    result = crew.kickoff()
    
    print("\n" + "="*80)
    print("BITCOIN TRADING ANALYSIS COMPLETE")
    print("="*80)
    print(result)
    print("="*80)
    
    # Check if HTML file was created and fix encoding if needed
    if os.path.exists("output.html"):
        # Re-read and rewrite with UTF-8 encoding to fix any encoding issues
        try:
            with open("output.html", "rb") as f:
                content = f.read()
            # Try to decode with different encodings
            html_content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    html_content = content.decode(encoding)
                    break
                except:
                    continue
            if html_content:
                # Rewrite with UTF-8
                with open("output.html", "w", encoding="utf-8", errors='replace') as f:
                    f.write(html_content)
                print("\nYour HTML report has been created: output.html")
                print("Open it in your browser to see the full analysis!\n")
            else:
                print("\nWarning: HTML file created but encoding may be incorrect\n")
        except Exception as e:
            print(f"\nWarning: Could not fix HTML encoding: {e}\n")
    else:
        print("\nWarning: output.html was not created\n")
    
    return result


if __name__ == "__main__":
    run_bitcoin_analysis()

