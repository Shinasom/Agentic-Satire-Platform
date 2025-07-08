import requests
import os
import random
import time
import json
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY") # For US News
MODEL_NAME = "llama3-70b-8192"
BACKEND_API_URL = "http://127.0.0.1:8000/api/articles"

# --- Base Agent ---
class GroqAgent:
    """The base agent for interacting with the Groq API."""
    def __init__(self, model_name=MODEL_NAME):
        self.model = model_name

    def run(self, prompt, temperature=0.8, max_tokens=1024, is_json=False):
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if is_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None

# --- Specialized Agents ---

class TrendSpotterAgent:
    """
    Fetches trending news topics by randomly choosing between
    GNews (India) and NewsAPI (US).
    """
    def __init__(self, gnews_key, newsapi_key):
        self.gnews_key = gnews_key
        self.newsapi_key = newsapi_key
        self.sources = []
        if gnews_key:
            self.sources.append(self._fetch_from_gnews)
        if newsapi_key:
            self.sources.append(self._fetch_from_newsapi)
        if not self.sources:
            raise ValueError("At least one news API key is required.")

    def _fetch_from_gnews(self):
        print("🕵️ Trend-Spotter Agent: Fetching trends from GNews (India)...")
        try:
            url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={self.gnews_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "articles" in data:
                return [a["title"] for a in data.get("articles", [])[:10]]
        except Exception as e:
            print(f"GNews API Error: {e}")
        return None

    def _fetch_from_newsapi(self):
        print("🕵️ Trend-Spotter Agent: Fetching trends from NewsAPI (US)...")
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.newsapi_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "ok" and data.get("articles"):
                return [a["title"] for a in data.get("articles", [])[:10] if a["title"] != "[Removed]"]
        except Exception as e:
            print(f"NewsAPI (US) Error: {e}")
        return None

    def run(self):
        chosen_source = random.choice(self.sources)
        articles = chosen_source()
        
        if articles:
            return articles
        
        print("⚠️ Trend-Spotter Agent: Using fallback trends.")
        return ["Cricket match results announced", "New smartphone released", "Government announces new policy"]


class TopicAnalysisAgent(GroqAgent):
    """Summarizes the core story behind a news headline for deeper context."""
    def run(self, trend):
        print("📊 Topic-Analysis Agent: Analyzing the core story...")
        prompt = f'''
        You are a news analyst. The following is a news headline: "{trend}"
        Your task is to provide a very brief, 2-sentence summary of the likely real story behind this headline.
        This summary will be used to generate satire, so focus on the key elements.
        '''
        return super().run(prompt, temperature=0.4, max_tokens=300)

class AngleBrainstormerAgent(GroqAgent):
    """Brainstorms multiple satirical angles for a given topic."""
    def run(self, trend):
        print("🧠 Angle-Brainstormer Agent: Developing satirical angles...")
        prompt = f'''
        A real news topic is: "{trend}"
        Brainstorm 3 distinct and funny satirical angles for this topic in the style of 'The Onion' or 'Faking News'.
        Present them as a numbered list. For example:
        1. [Angle 1]
        2. [Angle 2]
        3. [Angle 3]
        '''
        return super().run(prompt, temperature=0.8, max_tokens=500)

class HeadlineWriterAgent(GroqAgent):
    """Crafts a satirical headline from a specific angle."""
    def run(self, angle):
        print("✍️ Headline-Writer Agent: Crafting headline...")
        prompt = f'Create a satirical news headline in the style of The Onion or Faking News based on this specific angle: "{angle}". Make it absurd but plausible, max 12 words.'
        return super().run(prompt, temperature=0.9, max_tokens=100)

class ArticleWriterAgent(GroqAgent):
    """Writes or revises the satirical article."""
    def run(self, headline, feedback=None):
        if feedback:
            print("🔄 Article-Writer Agent: Revising article based on multi-critic feedback...")
            prompt = f'Revise the satirical article for the headline: "{headline}". You have received feedback from multiple critics. Rewrite the entire article, incorporating the following crucial points to make it better: "{feedback}".'
        else:
            print("📝 Article-Writer Agent: Writing high-quality first draft...")
            # CHANGED: Made dateline and expert names more general.
            prompt = f'''
            Write a professional 400-word satirical news article with this headline: "{headline}"
            
            Follow this structure precisely:
            1. Dateline: Start with a plausible location dateline (e.g., MUMBAI - or WASHINGTON D.C. -).
            2. Opening Paragraph: Cover the 5 Ws (Who, What, When, Where, Why) in a satirical way.
            3. Expert Quotes: Include quotes from at least 3 fake experts with plausible but funny-sounding names and titles.
            4. Statistics: Include one realistic-sounding but fake statistic relevant to the story.
            5. Tone: Maintain a serious, deadpan journalistic tone throughout.
            6. Conclusion: End with a serious-sounding concluding paragraph that adds a final satirical twist.
            '''
        return super().run(prompt, temperature=0.8, max_tokens=1024)

class HumorCriticAgent(GroqAgent):
    """A critic that focuses ONLY on the humor and comedic elements."""
    def run(self, headline, article):
        print("😂 Humor Critic Agent: Reviewing for comedic value...")
        prompt = f'''
        You are a comedy critic. Your only job is to assess if the article is funny.
        Headline: "{headline}"
        Article: "{article}"

        Focus ONLY on the humor. Are the jokes landing? Is the premise funny? Are the quotes witty?
        Provide one sentence of actionable feedback to make it funnier.
        Do NOT comment on style, grammar, or structure.
        If the humor is excellent and needs no improvement, respond ONLY with the word "Approved".
        '''
        return super().run(prompt, temperature=0.5, max_tokens=200)

class StyleCriticAgent(GroqAgent):
    """A critic that focuses ONLY on the journalistic style and tone."""
    def run(self, headline, article):
        print("👔 Style Critic Agent: Reviewing for tone and structure...")
        prompt = f'''
        You are an editor for a top-tier satirical publication. Your job is to ensure the article maintains a professional, "deadpan" journalistic tone, even when describing ridiculous events. The style should be serious, but the content can be absurd.

        Headline: "{headline}"
        Article: "{article}"

        Critique the article based ONLY on its style and tone.
        - Does it sound like a real, serious news report?
        - Is the language formal and objective, like a journalist would use?
        - Does it avoid breaking character by winking at the reader or becoming too silly in its phrasing?

        Provide one sentence of actionable feedback to improve the deadpan delivery.
        **Do NOT critique the absurdity of the events, quotes, or statistics themselves.** Your focus is on the *presentation*.
        If the style is perfect, respond ONLY with the word "Approved".
        '''
        return super().run(prompt, temperature=0.5, max_tokens=200)
    

class FinalEditorAgent(GroqAgent):
    """
    Acts as the final gate. It proofreads the article to remove all
    conversational filler and AI artifacts, then categorizes the clean text.
    """
    def run(self, headline, article):
        print("✅ Final Editor Agent: Performing final clean, proofread, and categorization...")
        # CHANGED: Made categories more general to fit both US and Indian news.
        prompt = f'''
        You are a stern, no-nonsense final copy editor for a satirical newspaper.
        Your only goal is to prepare the following article for publication.

        Article Headline: "{headline}"
        Article Draft: "{article}"

        Perform two tasks:

        TASK 1: RUTHLESSLY CLEAN THE ARTICLE.
        The draft may contain AI-generated artifacts, conversational filler, or meta-commentary. You must remove all of it.
        The final output text for this task MUST be ONLY the publishable article, starting with its dateline and ending with its final sentence.

        TASK 2: CATEGORIZE THE CLEANED ARTICLE.
        Based on the final, cleaned article text from Task 1, categorize it into ONE of the following options:
        Politics, World News, Business, Technology, Sports, Entertainment, Lifestyle, Science

        Return your response as a single, valid JSON object with two keys: "cleaned_article" and "category".
        '''
        return super().run(prompt, temperature=0.1, max_tokens=2048, is_json=True)


# --- The Orchestrator ---

class Coordinator:
    """Manages the entire multi-agent workflow."""
    def __init__(self):
        # CHANGED: Pass both API keys to the TrendSpotterAgent
        self.trend_spotter = TrendSpotterAgent(gnews_key=GNEWS_API_KEY, newsapi_key=NEWS_API_KEY)
        self.topic_analyzer = TopicAnalysisAgent()
        self.angle_brainstormer = AngleBrainstormerAgent()
        self.headline_writer = HeadlineWriterAgent()
        self.article_writer = ArticleWriterAgent()
        self.humor_critic = HumorCriticAgent()
        self.style_critic = StyleCriticAgent()
        self.final_editor = FinalEditorAgent()

    def run(self, max_revisions=2):
        print("\n--- 🎬 Coordinator: Starting Randomized International News Workflow ---\n")

        trends = self.trend_spotter.run()
        if not trends: return None, None, None
        trend = random.choice(trends)
        print(f'Coordinator: Selected trend -> "{trend}"\n')

        topic_summary = self.topic_analyzer.run(trend)
        if not topic_summary: topic_summary = trend
        print(f'Coordinator: Topic analysis -> "{topic_summary}"\n')

        angles_text = self.angle_brainstormer.run(topic_summary)
        if not angles_text: return None, None, None

        angles = [line.split('.', 1)[-1].strip() for line in angles_text.split('\n') if '.' in line]
        if not angles: return None, None, None
        angle = random.choice(angles)
        print(f'Coordinator: Chosen angle -> "{angle}"\n')

        headline = self.headline_writer.run(angle)
        if not headline: return None, None, None
        print(f'Coordinator: Generated headline -> "{headline}"\n')

        article = self.article_writer.run(headline)
        if not article: return None, None, None

        for i in range(max_revisions):
            print(f"--- Conducting critique round {i+1}/{max_revisions} ---")
            humor_feedback = self.humor_critic.run(headline, article)
            style_feedback = self.style_critic.run(headline, article)
            print(f'Coordinator: Humor Critic says -> "{humor_feedback}"')
            print(f'Coordinator: Style Critic says -> "{style_feedback}"\n')

            humor_approved = "Approved" in humor_feedback if humor_feedback else False
            style_approved = "Approved" in style_feedback if style_feedback else False

            if humor_approved and style_approved:
                print("--- ✅ Coordinator: Article Approved by critics! Moving to Final Editor. ---")
                break

            if i == max_revisions - 1:
                print("--- ⚠️ Coordinator: Max revisions reached. Sending to Final Editor as-is. ---")
                break

            combined_feedback = []
            if not humor_approved: combined_feedback.append(f"Humor Improvement: {humor_feedback}")
            if not style_approved: combined_feedback.append(f"Style Improvement: {style_feedback}")

            revision_prompt = " ".join(combined_feedback)
            print(f"Coordinator: Revision {i+1}/{max_revisions}. Sending back to writer.")
            article = self.article_writer.run(headline, feedback=revision_prompt)
            if not article: return None, None, None

        editor_json_response = self.final_editor.run(headline, article)
        if not editor_json_response:
            print("--- 🛑 Coordinator: Final Editor failed. Aborting workflow. ---")
            return None, None, None

        try:
            editor_data = json.loads(editor_json_response)
            final_article = editor_data.get("cleaned_article")
            final_category = editor_data.get("category", "General")

            if not final_article:
                 print("--- 🛑 Coordinator: Final Editor returned no article. Aborting. ---")
                 return None, None, None

            print(f"Coordinator: Final publishable article generated and categorized as '{final_category}'.")
            return headline, final_article, final_category

        except json.JSONDecodeError:
            print(f"--- 🛑 Coordinator: Failed to decode JSON from Final Editor. Response was: {editor_json_response} ---")
            return None, None, None

def submit_article_to_backend(headline, content, category):
    """Submits the final article to the backend with a disclaimer."""
    print("\n--- 📤 Submitting final article to the web app backend ---")
    disclaimer = (
        "\n\n---\n"
        "**Disclaimer:** This article is a work of satire and is entirely fictional. It is not intended to be taken as a factual account. "
        "Any resemblance to actual events, locales, or persons, living or dead, is purely coincidental."
    )
    final_content_with_disclaimer = content + disclaimer
    article_data = {
        "headline": headline,
        "content": final_content_with_disclaimer,
        "author": "AI Agent Team",
        "category": category,
    }
    try:
        response = requests.post(BACKEND_API_URL, json=article_data, timeout=15)
        response.raise_for_status()
        print("✅ Success! The new article is now a draft in your admin panel.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error submitting article to backend: {e}")

# --- Main Execution Block ---
if __name__ == "__main__":
    coordinator = Coordinator()
    final_headline, final_article, final_category = coordinator.run()

    if final_headline and final_article and final_category:
        submit_article_to_backend(final_headline, final_article, final_category)
    else:
        print("\n--- 🛑 Workflow failed. No article was submitted. ---")