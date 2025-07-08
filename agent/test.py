import requests
import os
from dotenv import load_dotenv

def test_gnews_api():
    """
    Fetches top headlines from India using the GNews API to verify the connection.
    """
    load_dotenv()
    # CHANGED: Using the new GNEWS_API_KEY from your .env file
    api_key = os.getenv("GNEWS_API_KEY")

    if not api_key:
        print("❌ Error: GNEWS_API_KEY not found in .env file.")
        return

    print("📡 Attempting to fetch news from India using GNews API...")

    # CHANGED: The URL now points to the GNews API endpoint
    # We are specifying country='in' and lang='en'
    url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={api_key}"

    try:
        response = requests.get(url, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        data = response.json()

        articles = data.get("articles")
        if articles:
            print("\n✅ Success! Fetched Top 5 Headlines from GNews:\n")
            for i, article in enumerate(articles[:5]):
                # The structure of the article object is slightly different in GNews
                print(f"{i+1}. {article['title']}")
        else:
            # GNews provides an error message in the 'errors' key if something is wrong
            if 'errors' in data:
                 print(f"❌ Error from GNews API: {data['errors'][0]}")
            else:
                 print("⚠️ The request was successful, but no articles were returned.")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error occurred: {http_err}")
        if response.status_code == 401:
            print("   (This often means your GNews API key is invalid or unauthorized.)")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_gnews_api()