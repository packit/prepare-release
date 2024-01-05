from click.testing import CliRunner

from prepare_release.prepare_release import prepare_release


def test_prepare_release():
    runner = CliRunner()
    result = runner.invoke(prepare_release, ["1.1", "."])
    assert "Preparing a new release" in result.output
