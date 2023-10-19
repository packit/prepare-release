#!/usr/bin/env python3

# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import re
from os import getenv
from pathlib import Path
from typing import Iterable, Optional

import click
from git import Commit, Repo
from ogr import GithubService

NOT_IMPORTANT_VALUES = ["n/a", "none", "none.", ""]
RELEASE_NOTES_TAG = "RELEASE NOTES"
RELEASE_NOTES_RE = f"{RELEASE_NOTES_TAG} BEGIN\r?\n(.+)\r?\n{RELEASE_NOTES_TAG} END"
PRE_COMMIT_CI_MESSAGE = "pre-commit autoupdate"


def get_relevant_commits(
    repository: Repo, ref: Optional[str] = None
) -> Iterable[Commit]:
    if not ref:
        tags = sorted(repository.tags, key=lambda t: t.commit.committed_datetime)
        if not tags:
            raise click.UsageError(
                "No REF was specified and the repo contains no tags, "
                "the REF must be specified manually."
            )
        ref = tags[-1]
    ref_range = f"{ref}..HEAD"
    return repository.iter_commits(rev=ref_range, merges=True)


def get_pr_id_old(message: str) -> str:
    # Merge pull request #1483 from majamassarini/fix/1357
    first_line = message.split("\n")[0]
    fourth_word = first_line.split(" ")[3]
    return fourth_word.lstrip("#")


def get_pr_id_new(message: str) -> str:
    # Sanitize changelog entry when updating dist-git spec file (#1841)
    first_line = message.split("\n")[0]
    if match := re.match(r"^.*\(\#(\d+)\)$", first_line):
        return match.group(1)
    return ""


def get_pr_id(message: str) -> str:
    """
    obtain PR ID
    """
    pr_id = get_pr_id_new(message)
    try:
        int(pr_id)
    except (ValueError, TypeError):
        pr_id = get_pr_id_old(message)

    return pr_id


def convert_message(message: str) -> Optional[str]:
    """Extract release note from the commit message,
    return None if there is no release note"""
    if RELEASE_NOTES_TAG in message:
        # new
        if found := re.findall(RELEASE_NOTES_RE, message, re.DOTALL):
            return found[0].strip()
        else:
            return None
    return None


def get_message_from_pr(repo: str, pr_id: str) -> str:
    service = GithubService(token=getenv("INPUT_TOKEN") or getenv("GITHUB_TOKEN"))
    project = service.get_project(namespace="packit", repo=repo)
    pr = project.get_pr(pr_id=int(pr_id))
    return pr.description


def get_changelog(commits: Iterable[Commit], repo: str, make_link: bool = False, include_pr: bool = True) -> str:
    changelog = ""
    for commit in commits:
        if PRE_COMMIT_CI_MESSAGE in commit.message:
            continue
        message = convert_message(commit.message)
        if message and message.lower() not in NOT_IMPORTANT_VALUES:
            pr_id = get_pr_id(commit.message)
            message = convert_message(get_message_from_pr(repo, pr_id))
            if make_link:
                url = f"https://github.com/packit/{repo}/pull/{pr_id}"
                pr_id = f"[{repo}#{pr_id}]({url})"
            else:
                pr_id = "#" + pr_id
            changelog += f"- {message}" (f" ({pr_id})\n" if include_pr else "\n")
    return changelog


@click.command(
    short_help="Get the changelog from the merge commits",
    help="""Get the changelog from the merge commits

    The script goes through the merge commits since the specified REF
    and gets the changelog entry from the commit message.
    In case no REF is specified, the latest tag is used.

    Currently, the changelog entry in the message is detected based on
    explicit marks of the beginning and the end denoted by
    `RELEASE NOTES BEGIN` and `RELEASE NOTES END` separators.
    """,
)
@click.option(
    "--git-repo",
    default=".",
    type=click.Path(dir_okay=True, file_okay=False),
    help="Git repository used for getting the changelog. "
    "Current directory is used by default.",
)
@click.argument("ref", type=click.STRING, required=False)
def changelog(git_repo, ref):
    repo = Repo(git_repo)
    print(get_changelog(get_relevant_commits(repo, ref), Path(repo.working_dir).name))


if __name__ == "__main__":
    changelog()
