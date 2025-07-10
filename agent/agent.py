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
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MODEL_NAME = "llama3-70b-8192"
BACKEND_API_URL = "http://127.0.0.1:8000/api/articles"

# --- Base Agent ---
class GroqAgent:
    """The base agent for interacting with the Groq API."""
    # CHANGED: The agent now accepts a specific model name on initialization.
    # We default to the fast model for any agent we don't specify.
    def __init__(self, model_name="llama-3.1-8b-instant"):
        self.model = model_name

    # The 'run' method remains the same
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
    #is used to fetch trending news from multiple sources and return a combined list.
    """
    Fetches trending news from all available sources and returns a combined list.
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
            
    # _fetch_from_gnews and _fetch_from_newsapi methods remain the same...
    def _fetch_from_gnews(self):
        # is used to fetch trending news from GNews API (India).
        print("🕵️ Trend-Spotter Agent: Fetching trends and content from GNews (India)...")
        try:
            url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={self.gnews_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            valid_articles = []
            if "articles" in data:
                for article in data["articles"]:
                    title = article.get("title")
                    content = article.get("content")
                    if title and content and len(title.split()) > 3:
                        valid_articles.append({"title": title, "content": content})
            return valid_articles[:10] if valid_articles else []
        except Exception as e:
            print(f"GNews API Error: {e}")
        return []

    def _fetch_from_newsapi(self):
        # is used to fetch trending news from NewsAPI (US).
        print("🕵️ Trend-Spotter Agent: Fetching trends and content from NewsAPI (US)...")
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.newsapi_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            valid_articles = []
            if data.get("status") == "ok" and data.get("articles"):
                for article in data["articles"]:
                    title = article.get("title")
                    content = article.get("content") or article.get("description")
                    if title and content and title != "[Removed]" and len(title.split()) > 3:
                        valid_articles.append({"title": title, "content": content})
            return valid_articles[:10] if valid_articles else []
        except Exception as e:
            print(f"NewsAPI (US) Error: {e}")
        return []

    def run(self):  
        all_articles = []
        for source_func in self.sources:
            # Add a delay between API calls to be safe
            time.sleep(1) 
            articles = source_func()
            if articles:
                all_articles.extend(articles)
        
        if all_articles:
            return all_articles
        
        print("⚠️ Trend-Spotter Agent: Using fallback trends.")
        return [
            {"title": "Cricket match results announced", "content": "The national cricket team has won a decisive victory in their latest match, with the captain scoring a century. Fans are celebrating the win across the country."},
            {"title": "New smartphone released", "content": "A major tech company has released its latest flagship smartphone, featuring a slightly improved camera and a new color option. Analysts predict it will sell millions of units despite its high price point."},
        ]


# --- History Management ---
# This remains a global constant for the file path
HISTORY_FILE = "used_articles.json"
#history file is used to track which articles have already been used.

class PotentialAssessorAgent(GroqAgent): #is used to intelligently select a new headline from the available articles.
    """
    An autonomous agent that intelligently selects a new headline,
    handling its own history checking and de-duplication recursively.
    """
    def _load_history(self):
        """Loads the history of used article titles."""
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _get_llm_choice(self, headlines): #is used to get a single choice from the LLM for a given list of headlines.
        """Gets a single choice from the LLM for a given list of headlines."""
        if not headlines:
            return None
            
        print(f"🧐 Potential-Assessor Agent: Evaluating {len(headlines)} headlines...")
        formatted_headlines = "\n".join(f"{i+1}. {headline}" for i, headline in enumerate(headlines))
        
        prompt = f'''
        You are the head writer for a satirical news show. Your job is to pick the most promising story to develop from the following list.

        [HEADLINES]
        {formatted_headlines}

        [INSTRUCTION]
        Respond with ONLY the number of the headline you choose. For example: 3
        '''
        return super().run(prompt, temperature=0.1, max_tokens=10)

    def run(self, all_articles):
        """
        Main execution method. Recursively selects a new, unused article.
        """
        used_headlines = self._load_history()
        
        # Filter out any articles whose titles are already in the history
        available_articles = [article for article in all_articles if article['title'] not in used_headlines]

        if not available_articles:
            print("--- 🛑 Potential-Assessor: No new, unused articles available to choose from.")
            return None # Return None if no new options are left

        # Get a choice from the LLM based on the available options
        available_titles = [article['title'] for article in available_articles]
        choice_str = self._get_llm_choice(available_titles)

        try:
            # Get the chosen article from the available list
            selected_index = int(choice_str.strip()) - 1
            if 0 <= selected_index < len(available_articles):
                chosen_article = available_articles[selected_index]
                print(f"Coordinator: Assessor selected -> \"{chosen_article['title']}\"")
                # Return the complete chosen article dictionary
                return chosen_article
            else:
                print("⚠️ Assessor returned an invalid index. Choosing a new one randomly.")
                return random.choice(available_articles)
        except (ValueError, TypeError):
            print("⚠️ Assessor returned a non-numeric response. Choosing a new one randomly.")
            return random.choice(available_articles)
    


class TopicAnalysisAgent(GroqAgent):#is used to summarize a raw news snippet into a clean, concise context. 
    """Summarizes a raw news snippet into a clean, concise context."""
    def run(self, story_content):
        print("📊 Topic-Analysis Agent: Summarizing real news content...")
        prompt = f'''
        You are a news analyst. Read the following news article snippet and summarize its core story in two concise sentences.
        This summary will be used to generate satire, so focus on the key, most important elements.

        Article Snippet to Summarize: "{story_content}"
        '''
        return super().run(prompt, temperature=0.4, max_tokens=300)

class AngleBrainstormerAgent(GroqAgent): #is used to brainstorm multiple satirical angles from a clean news summary.
    """Brainstorms multiple satirical angles from a clean news summary."""
    def run(self, summary):
        print("🧠 Angle-Brainstormer Agent: Developing satirical angles from summary...")
        prompt = f'''
        The following is a clean summary of a real news story: "{summary}"
        
        Brainstorm 3 distinct and funny satirical angles for this story in the style of 'The Onion' or 'Faking News'.
        Present them as a numbered list. For example:
        1. [Angle 1]
        2. [Angle 2]
        3. [Angle 3]
        '''
        return super().run(prompt, temperature=0.8, max_tokens=500)

class HeadlineWriterAgent(GroqAgent): #is used to craft a satirical headline from a specific angle.
    """Crafts a satirical headline from a specific angle."""
    def run(self, angle):
        print("✍️ Headline-Writer Agent: Crafting headline...")
        prompt = f'Create a satirical news headline in the style of The Onion or Faking News based on this specific angle: "{angle}". Make it absurd but plausible, max 12 words.'
        return super().run(prompt, temperature=0.9, max_tokens=100)

class ArticleWriterAgent(GroqAgent):#is used to write or revise the satirical article.

    """Writes or revises the satirical article."""
    def run(self, headline, angle, context, feedback=None):
        if feedback:
            print("🔄 Article-Writer Agent: Revising article based on multi-critic feedback...")
            # CHANGED: Added the full structural requirements to the revision prompt.
            prompt = f'''
            You are revising a satirical article. Rewrite the entire article based on the provided feedback.

            **Headline:** "{headline}"
            **Creative Angle (Your primary guide):** "{angle}"
            **Grounding Context (For details):** "{context}"
            **Feedback to Incorporate:** "{feedback}"

            While incorporating the feedback, you MUST adhere to the original angle and context, and you MUST follow this structure precisely:
            1. Dateline: An appropriate location for the context.
            2. Opening Paragraph: Cover the 5 Ws (Who, What, When, Where, Why) for the satirical story.
            3. Expert Quotes: Include quotes from at least 3 fake experts that support the angle.
            4. Statistics: Include one realistic-sounding but fake statistic.
            5. Tone: Maintain a serious, deadpan journalistic tone.
            6. Conclusion: End with a paragraph that adds a final satirical twist.
            '''
        else:
            print("📝 Article-Writer Agent: Writing high-quality first draft...")
            prompt = f'''
            Write a professional 400-word satirical news article.

            **Headline:** "{headline}"
            
            **Creative Angle (Your primary guide):** "{angle}"

            **Grounding Context (For details like location/names):** "{context}"
            
            You must write an article that perfectly executes the provided Creative Angle. Use the Grounding Context to inform the specific details, making the story feel real. Follow this structure precisely:
            1. Dateline: An appropriate location for the context.
            2. Opening Paragraph: Cover the 5 Ws (Who, What, When, Where, Why) for the satirical story.
            3. Expert Quotes: Include quotes from at least 3 fake experts that support the angle.
            4. Statistics: Include one realistic-sounding but fake statistic.
            5. Tone: Maintain a serious, deadpan journalistic tone.
            6. Conclusion: End with a paragraph that adds a final satirical twist.
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
        # CHANGED: Using a highly structured, forceful prompt to ensure compliance.
        prompt = f'''
        [SYSTEM INSTRUCTION]
        You are a style evaluation system for a satirical newspaper. Your function is to analyze the provided text against a set of rules and provide a single-line response.

        [RULES]
        1. Your ENTIRE output must be ONE of two things: the single word "Approved" OR a single sentence of actionable feedback.
        2. The feedback must ONLY address how to make the article's TONE more serious, professional, and "deadpan," like a real news report.
        3. DO NOT critique the humor, the absurdity of the events, or the content itself. Focus ONLY on the writing style.
        4. DO NOT use conversational language. Do not ask for the article. Do not greet. Execute the task based on the input below.

        [INPUT TEXT]
        Headline: "{headline}"
        Article: "{article}"

        [YOUR RESPONSE]
        '''
        return super().run(prompt, temperature=0.5, max_tokens=200)

class FinalEditorAgent(GroqAgent):
    """
    Acts as the final gate. It cleans the headline and article, removes all
    AI artifacts, then categorizes the clean text.
    """
    def run(self, headline, article):
        print("✅ Final Editor Agent: Performing final clean, proofread, and categorization...")
        prompt = f'''
        You are a stern, no-nonsense final copy editor for a satirical newspaper.
        Your only goal is to prepare the following for publication.

        Draft Headline: "{headline}"
        Draft Article: "{article}"

        Perform THREE tasks:

        TASK 1: RUTHLESSLY CLEAN THE HEADLINE.
        The draft headline may contain extra conversational text or explanations. Extract ONLY the core satirical headline itself. The result should be a short, single-line headline.

        TASK 2: RUTHLESSLY CLEAN THE ARTICLE.
        The draft may contain AI-generated artifacts, conversational filler, or meta-commentary. You must remove all of it.
        The final output text for this task MUST be ONLY the publishable article, starting with its dateline and ending with its final sentence.

        TASK 3: CATEGORIZE THE CLEANED ARTICLE.
        Based on the final, cleaned article text from Task 2, categorize it into ONE of the following options:
        Politics, World News, Business, Technology, Sports, Entertainment, Lifestyle, Science

        Return your response as a single, valid JSON object with three keys: "cleaned_headline", "cleaned_article", and "category".
        '''
        return super().run(prompt, temperature=0.1, max_tokens=2048, is_json=True)



def save_used_article(headline):
    """Saves a new, successfully used headline to the history file."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
            
    if headline not in history:
        history.append(headline)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)


# --- The Orchestrator ---

class Coordinator:
    """Manages the entire multi-agent workflow with specific models for each agent."""
    def __init__(self):
        # Define the models we'll use for clarity
        REASONING_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
        FAST_MODEL = "llama-3.1-8b-instant"

        # This agent doesn't use Groq, so no model needed.
        self.trend_spotter = TrendSpotterAgent(gnews_key=GNEWS_API_KEY, newsapi_key=NEWS_API_KEY)
        
        # --- Assign models based on task complexity ---

        # Agents for fast, simple, rule-based tasks use the FAST_MODEL
        self.topic_analyzer = TopicAnalysisAgent(model_name=FAST_MODEL)
        self.headline_writer = HeadlineWriterAgent(model_name=FAST_MODEL)
        self.final_editor = FinalEditorAgent(model_name=FAST_MODEL)

        # Agents for high-quality reasoning and creativity use the REASONING_MODEL
        self.potential_assessor = PotentialAssessorAgent(model_name=REASONING_MODEL)
        self.angle_brainstormer = AngleBrainstormerAgent(model_name=REASONING_MODEL)
        self.article_writer = ArticleWriterAgent(model_name=REASONING_MODEL)
        self.humor_critic = HumorCriticAgent(model_name=REASONING_MODEL)
        self.style_critic = StyleCriticAgent(model_name=REASONING_MODEL)


    def run(self, max_revisions=2):
        print("\n--- 🎬 Coordinator: Starting Autonomous Assessor Workflow ---\n")

        # Step 1: Get all possible trends from all sources
        all_trends = self.trend_spotter.run() #is used to fetch trending news from multiple sources and return a combined list.
        if not all_trends: return None, None, None
        time.sleep(2)  # Add delay

        # Step 2: Let the autonomous assessor handle selection and de-duplication
        # The Coordinator's logic is now much simpler.
        selected_trend = self.potential_assessor.run(all_trends)
        time.sleep(2) # Add delay
        
        if not selected_trend:
            print("--- 🛑 Coordinator: Assessor could not provide a suitable trend. Aborting. ---")
            return None, None, None
            
        trend_title = selected_trend['title']
        trend_content = selected_trend['content']
        print(f'Coordinator: Proceeding with trend -> "{trend_title}"\n')
        
        # Step 3: Summarize the real content to get a clean context
        context_source = trend_content if trend_content else trend_title
        clean_summary = self.topic_analyzer.run(context_source)
        if not clean_summary:
            print("Coordinator: Summarizer failed, falling back to raw content/title.")
            clean_summary = context_source
        print(f'Coordinator: Using clean summary as context -> "{clean_summary}"\n')
        time.sleep(2)

        # Step 4: Brainstorm Angles
        angles_text = self.angle_brainstormer.run(clean_summary)
        if not angles_text: return None, None, None
        angles = [line.split('.', 1)[-1].strip() for line in angles_text.split('\n') if '.' in line]
        if not angles: return None, None, None
        angle = random.choice(angles)
        print(f'Coordinator: Chosen angle -> "{angle}"\n')
        time.sleep(2)

        # Step 5: Write Headline
        headline = self.headline_writer.run(angle)
        if not headline: return None, None, None
        print(f'Coordinator: Generated headline -> "{headline}"\n')
        time.sleep(2)

        # Step 6: Write First Draft
        article = self.article_writer.run(headline, angle=angle, context=clean_summary)
        if not article: return None, None, None
        time.sleep(2)

        # Step 7: Multi-Critic Revision Loop
        for i in range(max_revisions):
            print(f"--- Conducting critique round {i+1}/{max_revisions} ---")
            humor_feedback = self.humor_critic.run(headline, article)
            time.sleep(2)
            style_feedback = self.style_critic.run(headline, article)
            time.sleep(2)
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
            article = self.article_writer.run(headline, angle=angle, context=clean_summary, feedback=revision_prompt)
            if not article: return None, None, None
            time.sleep(2)
        
        # Step 8: Final Polish and Categorization
        editor_json_response = self.final_editor.run(headline, article)
        if not editor_json_response:
            print("--- 🛑 Coordinator: Final Editor failed. Aborting workflow. ---")
            return None, None, None

        try:
            editor_data = json.loads(editor_json_response)
            final_headline = editor_data.get("cleaned_headline")
            final_article = editor_data.get("cleaned_article")
            final_category = editor_data.get("category", "General")

            if not final_article or not final_headline:
                 print("--- 🛑 Coordinator: Final Editor returned no article or headline. Aborting. ---")
                 return None, None, None

            # On success, the Coordinator triggers the save.
            save_used_article(trend_title)
            print(f"Coordinator: Successfully saved '{trend_title}' to history.")
            
            print(f"Coordinator: Final publishable article generated and categorized as '{final_category}'.")
            return final_headline, final_article, final_category

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