import os
import json
import openai
from github import Github


def get_pr_diff(repo, pr_number):
    """Fetches the diff of the pull request."""
    pr = repo.get_pull(pr_number)
    return pr.get_diff()


def get_project_guidelines():
    """Reads the team's coding guidelines from a local file."""
    try:
        with open('CODE_REVIEW_GUIDELINES.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No custom guidelines provided."


def get_ai_review(diff, guidelines):
    """Sends the code diff and guidelines to the AI model for a structured review."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """
    You are an expert code reviewer. Your task is to review a code diff based on project guidelines.
    Your feedback MUST be in a JSON array of comment objects. 
    Each object needs 'file_path', 'line_number', and 'comment'.
    The 'line_number' must be the line number within the diff file itself, not the original file.
    If you find no issues, return an empty JSON array: `[]`.
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
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    return response.choices[0].message.content


def post_review_to_github(repo, pr_number, review_comments):
    """Posts the AI's feedback as line-specific comments on the GitHub PR."""
    pr = repo.get_pull(pr_number)

    for comment in review_comments:
        try:
            file_path = comment['file_path']
            line_number = comment['line_number']
            comment_body = f"**AI Reviewer Suggestion**:\n\n{comment['comment']}"
            commit = pr.get_commits().reversed[0]

            pr.create_review_comment(
                body=comment_body,
                commit_id=commit.sha,
                path=file_path,
                line=line_number
            )
            print(f"Posted comment to {file_path} at line {line_number}")
        except Exception as e:
            print(f"Could not post comment: {e}")


def main():
    """Main function to orchestrate the code review process."""
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = int(os.getenv("GITHUB_REF").split('/')[2])

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    print("Fetching PR diff...")
    diff = get_pr_diff(repo, pr_number)

    print("Fetching guidelines...")
    guidelines = get_project_guidelines()

    print("Sending to AI for review...")
    review_json = get_ai_review(diff, guidelines)

    review_data = json.loads(review_json)

    comments = review_data.get("reviews", [])
    if comments:
        print(f"AI found {len(comments)} issues. Posting to GitHub...")
        post_review_to_github(repo, pr_number, comments)
    else:
        print("AI found no issues.")


if __name__ == "__main__":
    main()