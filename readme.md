# Reddit Auto-Posting Bot (🚨 Use at Your Own Risk!)

## 🔑 Setting Up Your Reddit Credentials
Before using this bot, you need Reddit API credentials. Follow these steps:

1. **Create a Reddit App:**
   - Go to [Reddit Developer Portal](https://www.reddit.com/prefs/apps).
   - Click **Create App** at the bottom.
   - Choose "script" as the type.
   - Fill in the app details (Name, Description, Redirect URI: `http://localhost`).
   - Submit and copy your `client_id` and `client_secret`.

2. **Create a `.env` File**
   - In the project directory, create a `.env` file.
   - Add the following credentials:
     ```
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     REDDIT_USERNAME=your_username
     REDDIT_PASSWORD=your_password
     OPENAI_API_KEY=your_openai_api_key
     ```

## 📌 How This Bot Works
This bot automates posting content to multiple subreddits while avoiding plagiarism through subtle title rephrasing. Here's the workflow:

1. **Extracting Post Data:**
   - The bot fetches a post using its Reddit post ID.
   - It retrieves the title, text content, and image (if available).
   - If an image is present, it downloads and saves it.

2. **Generating Rephrased Titles:**
   - The bot counts the number of target subreddits (`n`).
   - It asks OpenAI to generate `n` subtly rephrased versions of the title.
   - OpenAI returns a JSON object containing a list of these reworded titles.

3. **Posting to Subreddits:**
   - The bot iterates over the list of target subreddits.
   - It fetches available flair templates (if accessible) and selects the first flair.
   - It posts the content with a rephrased title and flair (if available).
   - A random sleep interval between **100-150 seconds** is used between posts.
   - The bot catches errors (such as permission issues) and continues posting instead of crashing.

4. **Completion Report:**
   - After posting, it prints the number of successful and failed posts.

## 🔧 Possible Improvements
This bot works but has **several limitations** that can be improved:
- **Random Flair Selection**: Currently, it selects the first available flair. AI could be used to analyze the title and choose the most relevant flair.
- **More Human-like Delays**: The current random sleep interval is basic. Implementing variable post timings based on subreddit activity could reduce detection risks.
- **Better Error Handling**: Some errors (e.g., subreddit bans, rate limits) could be handled more gracefully.
- **Account Safety Mechanisms**: Implementing different Reddit accounts for different subreddits and using proxies could help avoid bans.

## ⚠️ WARNING: Use at Your Own Risk!
🚨 **This bot works, but it gets accounts suspended!** 🚨
- Reddit has strict anti-bot policies, and automated posting can lead to account suspensions.
- Using this bot on public subreddits **without permissions** may result in subreddit bans.
- Always test in private or bot-friendly subreddits.

**If you use this bot as it is, be prepared to lose your account. You have been warned.** ☠️

---

**Final Note:** The code is documented and structured for improvement. If you want to refine it, go ahead—but be mindful of Reddit's policies. 🚀