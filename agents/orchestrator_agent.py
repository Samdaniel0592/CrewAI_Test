# OrchestratorAgent: Coordinates the process

def run_pipeline(jira_api_key, openai_api_key):
    # 1. Get user stories from JIRA
    from agents.testcase_generator_agent import get_user_stories, generate_test_cases
    from agents.testcase_validator_agent import validate_test_cases
    from agents.copilot_agent import generate_playwright_scripts, generate_github_actions

    user_stories = get_user_stories(jira_api_key)
    test_cases = generate_test_cases(user_stories, openai_api_key)
    validated_cases = validate_test_cases(test_cases)
    playwright_scripts = generate_playwright_scripts(validated_cases)
    github_actions = generate_github_actions(playwright_scripts)
    return {
        'user_stories': user_stories,
        'test_cases': test_cases,
        'validated_cases': validated_cases,
        'playwright_scripts': playwright_scripts,
        'github_actions': github_actions
    }
