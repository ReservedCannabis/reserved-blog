
import openai
import datetime
from google_sheets_logger import log_to_sheet
from config import OPENAI_API_KEY

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

blog_topics = [
    "Same-Day Weed Delivery in Etobicoke – What You Need to Know",
    "Waterloo’s Top Cannabis Products for First-Time Buyers",
    "How to Choose the Right THC vs CBD Ratio for You"
]

def generate_blog_post(topic):
    prompt = f"Write a 500-word SEO-optimized blog post titled '{topic}' for a legal cannabis retail site in Ontario. Make it informative, include keywords naturally, and format using basic HTML tags."
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def save_post(topic, content):
    filename = "posts/" + topic.lower().replace(" ", "_").replace("–", "-").replace(",", "").replace("'", "") + ".html"
    with open(filename, "w") as f:
        f.write(content)

if __name__ == "__main__":
    import os
    os.makedirs("posts", exist_ok=True)
    for topic in blog_topics:
        content = generate_blog_post(topic)
        save_post(topic, content)
        log_to_sheet("generate_local_content", topic, "Post Created", datetime.datetime.now().isoformat())
