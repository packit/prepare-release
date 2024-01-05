#!/usr/bin/python3

import os
import click
from pathlib import Path
from typing import Optional

from git import Repo
from prepare_release.changelog import get_changelog, get_relevant_commits
from specfile import Specfile
from specfile.macro_definitions import CommentOutStyle


@click.command()
@click.option("--prerelease-suffix-pattern")
@click.option("--prerelease-suffix-macro")
@click.argument("version")
@click.argument("specfile_path")
def prepare_release(
    version: str,
    specfile_path: str,
    prerelease_suffix_pattern: Optional[str] = None,
    prerelease_suffix_macro: Optional[str] = None,
):
    click.echo("Preparing a new release")
    repo = Repo()
    repo_name = (
        os.getenv("GITHUB_REPOSITORY", "/").split("/")[1] or Path(repo.working_dir).name
    )
    new_entry = get_changelog(get_relevant_commits(repo), repo_name)
    changelog_file = Path("CHANGELOG.md")
    current_changelog = changelog_file.read_text()
    changelog_file.write_text(f"# {version}\n\n{new_entry}\n{current_changelog}")
    for path in specfile_path.split(","):
        with Specfile(path, autosave=True) as specfile:
            specfile.update_version(
                version,
                prerelease_suffix_pattern,
                prerelease_suffix_macro,
                CommentOutStyle.HASH,
            )
            specfile.release = "1"
            specfile.add_changelog_entry(
                f"- New upstream release {version}",
                author="Packit Team <hello@packit.dev>",
            )


if __name__ == "__main__":
    prepare_release()
