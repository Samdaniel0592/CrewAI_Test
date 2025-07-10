import os
import requests
import openai
import logging
import base64
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Read credentials and config from environment
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Fetch user stories from JIRA using Basic Auth
def fetch_user_stories():
    auth = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }
    jql = f"project={JIRA_PROJECT_KEY} AND issuetype=Story ORDER BY created DESC"
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={jql}&fields=summary"
    logging.info(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    logging.info(f"Status code: {response.status_code}")
    response.raise_for_status()
    issues = response.json().get('issues', [])
    stories = [
        {'id': issue['key'], 'summary': issue['fields']['summary']} for issue in issues
    ]
    logging.info(f'Fetched user stories: {stories}')
    return stories

# Generate test cases for each user story using OpenAI LLM
# Returns a list of dicts: {story_id, test_case}
def generate_test_cases(stories):
    logging.info('Generating test cases using OpenAI...')
    test_cases = []
    for story in stories:
        prompt = f"Generate step-by-step test cases for the following user story: {story['summary']}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a QA test case generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        test_case = response.choices[0].message.content.strip()
        test_cases.append({'story_id': story['id'], 'test_case': test_case})
    #logging.info(f'Generated test cases: {test_cases}')
    return test_cases

# Save all generated test cases to a text file for user review
def save_test_cases_to_file(test_cases, filename="generated_test_cases.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for case in test_cases:
            f.write(f"Story ID: {case['story_id']}\n")
            f.write(case['test_case'])
            f.write("\n\n" + "-"*40 + "\n\n")
    logging.info(f"Test cases saved to {filename}")

# Validate test cases for non-empty content
def validate_test_cases(test_cases):
    validated = []
    for case in test_cases:
        is_valid = bool(case['test_case'])
        validated.append({**case, 'is_valid': is_valid, 'validation_notes': 'Valid' if is_valid else 'Invalid'})
    return validated

# Main pipeline execution
if __name__ == "__main__":
    try:
        # Step 1: Fetch user stories from JIRA
        stories = fetch_user_stories()
        # Step 2: Generate test cases using OpenAI
        test_cases = generate_test_cases(stories)
        # Step 3: Validate test cases
        validated_cases = validate_test_cases(test_cases)
        # Step 4: Print all results as JSON
        output = {
            "user_stories": stories,
            "test_cases": test_cases,
            "validated_cases": validated_cases
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        # Step 5: Save test cases to a text file
        save_test_cases_to_file(test_cases)
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")