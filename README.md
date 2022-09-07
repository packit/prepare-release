# packit/prepare-release

GitHub Action to prepare a new release, which includes:

- generate a new changelog entry in `CHANGELOG.md`
- update the version in the specfile
- update `%changelog` in the specfile

Inputs:

- `version`: version string to be used in for the release
- `specfiles`: comma separated paths of the specfiles to be updated
