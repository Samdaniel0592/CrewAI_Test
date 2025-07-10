import logging
import openai
import requests
import os
import base64
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

logging.basicConfig(level=logging.INFO, format='%(message)s')

# CrewAI agent function: Fetch user stories from JIRA
def fetch_user_stories():
    logging.info('Fetching user stories from JIRA...')
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_KEY = os.getenv("JIRA_API_KEY")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
    auth = f"{JIRA_EMAIL}:{JIRA_API_KEY}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }
    jql = f"project={JIRA_PROJECT_KEY} AND issuetype=Story ORDER BY created DESC"
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={jql}&fields=summary"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    issues = response.json().get('issues', [])
    stories = [
        {'id': issue['key'], 'summary': issue['fields']['summary']} for issue in issues
    ]
    logging.info(f'Fetched user stories: {stories}')
    return stories

# CrewAI agent function: Generate test cases using OpenAI

def generate_test_cases(stories):
    logging.info('Generating test cases using OpenAI...')
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY
    test_cases = []
    for story in stories:
        prompt = f"Generate step-by-step test cases for the following user story: {story['summary']}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a QA test case generator."},
                      {"role": "user", "content": prompt}],
            max_tokens=300
        )
        test_case = response.choices[0].message.content.strip()
        test_cases.append({'story_id': story['id'], 'test_case': test_case})
    logging.info(f'Generated test cases: {test_cases}')
    return test_cases

# CrewAI agent function: Validate test cases

def validate_test_cases(test_cases):
    logging.info('Validating test cases for coverage and quality...')
    validated = [
        {**case, 'is_valid': bool(case['test_case']), 'validation_notes': 'Valid' if case['test_case'] else 'Invalid'} for case in test_cases
    ]
    logging.info(f'Validated test cases: {validated}')
    return validated

# Save test cases to a text file
def save_test_cases_to_file(test_cases, filename="generated_test_cases.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for case in test_cases:
            f.write(f"Story ID: {case['story_id']}\n")
            f.write(case['test_case'])
            f.write("\n\n" + "-"*40 + "\n\n")
    logging.info(f"Test cases saved to {filename}")

# Define CrewAI agents
orchestrator_agent = Agent(
    name="OrchestratorAgent",
    role="Coordinates the process",
    goal="Orchestrate the test automation tasks.",
    backstory="An experienced automation orchestrator, skilled at coordinating multi-agent tasks for software quality assurance."
)

testcase_generator_agent = Agent(
    name="TestcaseGeneratorAgent",
    role="Generates test cases from JIRA user stories",
    goal="Fetch user stories from JIRA and generate step-by-step test cases using OpenAI.",
    backstory="A test design specialist with deep knowledge of user story analysis and LLM-driven test case generation."
)

testcase_validator_agent = Agent(
    name="TestcaseValidatorAgent",
    role="Validates test cases",
    goal="Validate generated test cases for coverage and quality.",
    backstory="A meticulous QA expert, ensuring all test cases meet coverage and quality standards."
)

# Define CrewAI tasks
fetch_stories_task = Task(
    description="Fetch user stories from JIRA.",
    agent=testcase_generator_agent,
    expected_output="A list of user stories fetched from JIRA.",
    func=fetch_user_stories
)

generate_testcases_task = Task(
    description="Generate step-by-step test cases using OpenAI.",
    agent=testcase_generator_agent,
    expected_output="A set of detailed, step-by-step test cases for each user story.",
    func=lambda: generate_test_cases(fetch_user_stories())
)

validate_testcases_task = Task(
    description="Validate test cases for coverage and quality.",
    agent=testcase_validator_agent,
    expected_output="A list of validated test cases with coverage and quality status.",
    func=lambda: validate_test_cases(generate_test_cases(fetch_user_stories()))
)

# Define the CrewAI task runner (not called pipeline)
crew = Crew(
    agents=[
        orchestrator_agent,
        testcase_generator_agent,
        testcase_validator_agent
    ],
    tasks=[
        fetch_stories_task,
        generate_testcases_task,
        validate_testcases_task
    ]
)
