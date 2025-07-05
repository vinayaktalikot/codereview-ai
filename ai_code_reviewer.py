import os
import json
import openai
import requests
from github import Github

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

def get_pr_diff(repo, pr_number, github_token):
    """Fetches the diff of the pull request using its diff_url"""
    pr = repo.get_pull(pr_number)
    diff_url = pr.diff_url
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3.diff"}
    response = requests.get(diff_url, headers=headers)
    response.raise_for_status()
    return response.text


def get_project_guidelines():
    try:
        with open('CODE_REVIEW_GUIDELINES.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("INFO: CODE_REVIEW_GUIDELINES.md not found")
        return "No custom guidelines provided."


def get_ai_review(diff, guidelines):
    if DEBUG_MODE:
        print("--- DEBUG MODE: USING MOCK AI RESPONSE ---")
        return json.dumps({
            "reviews": [
                {
                    "file_path": "app/main.py",
                    "comment": "Guideline Violated: Hardcoded Secrets. The API key is hardcoded directly in the source code. This is a major security risk and should be loaded from a secure environment variable or secrets manager."
                },
                {
                    "file_path": "app/main.py",
                    "comment": "Guideline Violated: SQL Injection. The database query is constructed using an f-string with raw user input. This makes it vulnerable to SQL Injection attacks. Please use parameterized queries to fix this."
                }
            ]
        })

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt = """
    You are an expert code reviewer. Your task is to review a code diff based on project guidelines.
    Your feedback MUST be in a JSON object containing a single key "reviews" which is an array of comment objects.
    Each comment object needs 'file_path' and 'comment'. Do not include line numbers.
    If you find no issues, return an empty array: `{"reviews": []}`.
    """
    user_prompt = f"""
    **Project Guidelines:**
    ```markdown
    {guidelines}
    ```

    **Code Diff to Review:**
    ```diff
    {diff}
    ```
    Provide your review in the specified JSON format.
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return response.choices[0].message.content


def post_review_to_github(repo, pr_number, review_comments):
    """
    Posts the AI's feedback as a single, consolidated review comment on the PR
    """
    pr = repo.get_pull(pr_number)

    comment_body = "## AI Code Review\n\n"
    comment_body += "I've reviewed the changes and found the following issues based on our guidelines:\n\n"

    for comment in review_comments:
        comment_body += f"--- \n"
        comment_body += f"**File:** `{comment['file_path']}`\n\n"
        comment_body += f"**Issue:** {comment['comment']}\n\n"

    if not review_comments:
        print("No comments to post.")
        return

    try:
        pr.create_issue_comment(comment_body)
        print(f"Successfully posted a review summary with {len(review_comments)} issues")
    except Exception as e:
        print(f"Failed to create review comment: {e}")


def main():
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("PR_NUMBER"))

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    print("Fetching PR diff--->")
    diff = get_pr_diff(repo, pr_number, github_token)

    print("Fetching guidelines -->")
    guidelines = get_project_guidelines()

    print("Sending to AI for review -->")
    review_json_string = get_ai_review(diff, guidelines)

    print("\n AI Response --->")
    print(review_json_string)
    print("-------------------\n")

    review_data = json.loads(review_json_string)
    comments = review_data.get("reviews", [])
    if comments:
        print(f"Found {len(comments)} issues. Posting to GitHub")
        post_review_to_github(repo, pr_number, comments)
    else:
        print("AI found no issues to comment on.")


if __name__ == "__main__":
    main()