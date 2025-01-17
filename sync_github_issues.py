import os
import urllib.parse
import datetime

from github import Github, GithubException
import ps
from util import utc_now

# Number of days before the next event that we should create an RSVP issue
DAY_LIMIT = 14


def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not repo:
        raise ValueError("GITHUB_REPOSITORY is required")

    github = Github(token)
    repository = github.get_repo(repo)

    next_event = next(ps.next_events())
    found_next_event_slug = False
    print(f"Upserting github issue for {next_event.slug}...")

    # We would prefer to be filtering on the "event" label here but currently
    # the github actions bot token can't add new labels due to a bug:
    # https://github.com/orgs/community/discussions/149877
    for issue in repository.get_issues(state="all"):  # , labels=["event"]
        print(f"* Processing issue {issue.id} - {issue.html_url}")

        # This is horrid, but we _always_ have "standards" in the slug
        ps_labels = [label.name for label in issue.labels if "standards" in label.name]
        event_slug = None
        if ps_labels:
            event_slug = ps_labels[0]

        print(f"* Found {issue.state} issue for '{issue.title}' ({event_slug})")

        # We prefer matching on the event slug in case title changes upstream
        if next_event.slug == event_slug or next_event.title == issue.title:
            found_next_event_slug = True

            # If someone accidentally closes the issue, reopen it
            if issue.state == "closed":
                print("* Reopening closed issue")
                issue.edit(state="open")

            # Ensure this is still pinned
            set_issue_pin(github, issue, pin=True)

            # Update the event title and description
            issue.edit(
                title=next_event.title,
                body=get_issue_body(next_event),
                labels=["event", next_event.slug],
            )

        else:
            # If this issue is open, but it's not for the next event, close and unpin it
            if issue.state == "open":
                print("* Closing issue")
                issue.edit(state="closed")
                set_issue_pin(github, issue, pin=False)

    # If we've not found the current event and it's within the day limit, create it
    if not found_next_event_slug:
        if next_event.start_dt > utc_now() + datetime.timedelta(days=DAY_LIMIT):
            print(
                f"* {next_event.slug} is not within {DAY_LIMIT} days, skipping creation for now"
            )
        else:
            print(f"* Creating issue for {next_event.slug}")

            new_issue = repository.create_issue(
                title=next_event.title,
                body=get_issue_body(next_event),
                labels=["event", next_event.slug],
            )

            set_issue_pin(github, new_issue, pin=True)
            print(f"Created & pinned issue for {next_event.slug}: ", new_issue.html_url)


def get_issue_body(event):
    encoded_address = urllib.parse.quote(event.location_and_address)
    return f"""
[{event.title}](https://london.pubstandards.com/event/{event.slug}) will be held on {event.pretty_date} at [{event.location}](http://maps.google.co.uk/maps?q={encoded_address}).

**To let people know you're coming, react to this Github Issue with the following emoji**:
* 👍 - Attending
* 👀 - Interested
* 👎 - Not attending

The [event page](https://london.pubstandards.com/event/{event.slug}) will update with your status and avatar within a few hours.
"""  # noqa: E501


def set_issue_pin(github, issue, pin):
    operation = "pinIssue" if pin else "unpinIssue"

    # Pygithub only gained a property for the graphql node_id on Issues last
    # week so we have to extract it's innards
    issue_node_id = issue._rawData["node_id"]

    # The github graphql API will throw an error if you try to pin/unpin an
    # already pinned/unpinned issue, and the only way to check if something is
    # already pinned is to do _another_ graphql query as tis state is not
    # exposed in the REST API, so we just ignore errors here, who cares
    try:
        github.requester.graphql_named_mutation(
            mutation_name=operation,
            mutation_input={"issueId": issue_node_id},
            output_schema="issue { isPinned }",
        )
    except GithubException:
        pass


if __name__ == "__main__":
    main()
