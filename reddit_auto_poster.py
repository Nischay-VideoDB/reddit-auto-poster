import praw
import time
import requests
import json
import openai
import os
import re
from dotenv import load_dotenv
import prawcore  # Required for handling Reddit API exceptions
import random  # For adding random sleep intervals

# Load environment variables from .env file
load_dotenv()

# Initialize Reddit API Client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
)

# Initialize OpenAI API Client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

def fetch_post(post_id):
    """Fetches Reddit post details using the post ID."""
    print("📝 Fetching Post Data...\n")
    submission = reddit.submission(id=post_id)

    post_data = {
        "title": submission.title,
        "text": getattr(submission, "selftext", ""),
        "image_url": None,
        "image_path": None,
    }

    # If the post contains an image, download it
    if hasattr(submission, "url") and submission.url.endswith(('jpg', 'png', 'jpeg')):
        post_data["image_url"] = submission.url
        post_data["image_path"] = download_image(post_data["image_url"])

    print(f"\tTitle: {post_data['title']}\n")
    print("✅ Post Data Fetched\n")
    return post_data

def rephrase_title(post_data, n):
    """
    Uses OpenAI to subtly rephrase the post title into `n` distinct forms.
    Ensures the meaning remains intact and maintains a similar length.
    """
    prompt = (
        f"Subtly rephrase the following title into {n} distinct forms. "
        f"Keep the meaning intact and do not change the length significantly. "
        f"Strictly return a JSON object with exactly one key: 'title', which maps to a list of {n} rephrased strings. "
        f"Do not include any extra text or explanation.\n\n"
        f"Example response format:\n"
        f"{{\"title\": [\"Rephrased Title 1\", \"Rephrased Title 2\", \"Rephrased Title 3\"]}}\n\n"
        f"Title: {post_data['title']}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        ai_response = response.choices[0].message.content.strip()

        # Debugging: Print the raw response
        print("\n🔍 RAW OpenAI Response:", ai_response, "\n")

        # Remove markdown-style JSON formatting if present
        if ai_response.startswith("```json"):
            ai_response = re.sub(r"```json\n|\n```", "", ai_response).strip()

        # Convert the response to a Python dictionary
        rephrased_data = json.loads(ai_response)
        rephrased_titles = rephrased_data.get("title", [])

        if not isinstance(rephrased_titles, list) or len(rephrased_titles) != n:
            print(f"⚠️ Warning: Expected a JSON array of length {n}, but got: {rephrased_titles}")
            return []
        return rephrased_titles

    except (OpenAIError, json.JSONDecodeError, Exception) as e:
        print(f"⚠️ OpenAI error: {e}")
        return []

def post_to_subreddits(post_id, target_subreddits, sleep):
    """Posts the extracted content to each target subreddit with rephrased titles."""
    post_data = fetch_post(post_id)
    n = len(target_subreddits)
    rephrased_titles = rephrase_title(post_data, n)
    
    if not rephrased_titles or len(rephrased_titles) != n:
        print("❌ Rephrased titles not available in expected number. Aborting posting process.")
        return

    print("📝 Starting the posting process...\n")
    total, count, failed, success = n, 0, 0, 0

    for i, subreddit_name in enumerate(target_subreddits):
        subreddit = reddit.subreddit(subreddit_name)
        
        # Handle subreddit flair fetching gracefully
        try:
            flair_templates = list(subreddit.flair.link_templates)
            flair_id = flair_templates[0]["id"] if flair_templates else None
        except prawcore.exceptions.Forbidden:
            print(f"\t⚠️ No permission to fetch flairs for r/{subreddit_name}. Proceeding without flair.")
            flair_id = None
        
        rephrased_title = rephrased_titles[i]
        count += 1
        try:
            print(f"\n\t{count}/{total} Posting → r/{subreddit_name}")
            if count != 1:
                random_sleep = random.randint(100, 150)  # Random sleep interval to mimic human behavior
                for remaining in range(random_sleep, 0, -1):
                    print(f"\t\t⏳ Remaining time: {remaining} seconds", end='\r')
                    time.sleep(1)
            
            if post_data["image_url"]:
                subreddit.submit_image(title=rephrased_title, image_path=post_data["image_path"], flair_id=flair_id)
            else:
                subreddit.submit(title=rephrased_title, selftext=post_data["text"], flair_id=flair_id)
            
            print(f"\t✅ Posted to → r/{subreddit_name}")
            success += 1

        except Exception as e:
            print(f"\t❌ Failed to post in r/{subreddit_name}: {e}")
            failed += 1
    
    print(f"\n✨ Execution Completed ✨")
    print(f"✅ Successful Posts: {success}")
    print(f"❌ Failed Posts: {failed}")

def download_image(image_url):
    """Downloads an image and saves it locally."""
    image_path = "temp_image.jpg"
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(image_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print("\tImage downloaded successfully.")
        return image_path
    except requests.exceptions.RequestException as e:
        print(f"\t⚠️ Error downloading image: {e}")
        return None

if __name__ == "__main__":
    post_id = "Reddit Post ID"  # Set post ID
    target_subreddits = ["subreddit_1", "subreddit_2", "subreddit_3"]
    sleep = 120  # Sleep time between posts (in seconds)
    post_to_subreddits(post_id, target_subreddits, sleep)
