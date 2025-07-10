import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def fetch_user_stories():
    auth = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }
    jql = f"project={JIRA_PROJECT_KEY} AND issuetype=Story ORDER BY created DESC"
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={jql}&fields=summary"
    print(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()
    issues = response.json().get('issues', [])
    stories = [
        {'id': issue['key'], 'summary': issue['fields']['summary']} for issue in issues
    ]
    print(f'Fetched user stories: {stories}')
    return stories

if __name__ == "__main__":
    fetch_user_stories()
