# packit/prepare-release

GitHub Action to prepare a new release, which includes:

- generate a new changelog entry in `CHANGELOG.md`
- update the version in the specfile
- update `%changelog` in the specfile

Inputs:

- `version`: version string to be used in for the release
- `specfiles`: comma separated paths of the specfiles to be updated
- `token`: a `repo` scoped [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token);
  defaults to [`GITHUB_TOKEN` secret](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) if missing
