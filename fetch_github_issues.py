from collections import defaultdict
import os
import json
from github import Github
import slug


def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not repo:
        raise ValueError("GITHUB_REPOSITORY is required")

    # All RSVP issues are in pubstandards-london-rsvp, doing it this way means
    # that if you have a fork of this repo you're working on, GHA will
    # automatically use your own fork of the -rsvp repo too
    repo = repo + "-rsvp"

    github = Github(token)
    repository = github.get_repo(repo)

    # We would prefer to be filtering on the "event" label here but currently
    # the github actions bot token can't add new labels due to a bug:
    # https://github.com/orgs/community/discussions/149877
    reaction_data = defaultdict(dict)
    for issue in repository.get_issues(state="all"):  # , labels=["event"]
        print(f"* Processing issue {issue.id} - {issue.html_url}")

        # This is horrid, but we _always_ have "standards" in the slug
        ps_labels = [label.name for label in issue.labels if "standards" in label.name]
        if ps_labels:
            event_slug = ps_labels[0]
        else:
            # Fall back to using the issue title as a slug, in case this issue
            # doesn't have a label for the event due to the aforementioned
            # github actions labelling bug
            print("* No slug label, falling back to generating slug from issue title")
            event_slug = slug.slug(issue.title)

        reaction_data[event_slug]["url"] = issue.html_url

        reactions = list(issue.get_reactions())
        print(f"* Found {len(reactions)} reactions for {event_slug}")

        reaction_data[event_slug]["reactions"] = defaultdict(list)
        for reaction in reactions:
            user_data = {
                "username": reaction.user.login,
                "name": reaction.user.name,
                "avatar_url": reaction.user.avatar_url,
            }
            reaction_data[event_slug]["reactions"][reaction.content].append(user_data)

    # Write out all the reactions + issue data so the webside can read it
    with open("gh_issue_reactions.json", "w") as f:
        json.dump(reaction_data, f)


if __name__ == "__main__":
    main()
