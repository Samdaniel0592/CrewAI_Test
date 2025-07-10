# TestcaseGeneratorAgent: Gets user stories from JIRA, creates test cases via OpenAI LLM
import requests
import openai

def get_user_stories(jira_api_key):
    # Placeholder: Replace with actual JIRA API call
    # Example: Fetch issues from a JIRA project
    headers = {'Authorization': f'Bearer {jira_api_key}'}
    # url = 'https://your-domain.atlassian.net/rest/api/3/search?...'
    # response = requests.get(url, headers=headers)
    # return response.json()['issues']
    return [
        {'id': 'STORY-1', 'summary': 'User can log in'},
        {'id': 'STORY-2', 'summary': 'User can reset password'}
    ]

def generate_test_cases(user_stories, openai_api_key):
    openai.api_key = openai_api_key
    test_cases = []
    for story in user_stories:
        prompt = f"Generate step-by-step test cases for the following user story: {story['summary']}"
        # response = openai.Completion.create(...)
        # test_case = response['choices'][0]['text']
        test_case = f"Test case for {story['summary']} (mocked)"
        test_cases.append({'story_id': story['id'], 'test_case': test_case})
    return test_cases
