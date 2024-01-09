import pytest


class TestSuiteServerCli:
    @pytest.mark.skipif(reason="Argilla server is installed", condition=False)
    def test_server_cli_is_present(self, cli_runner: "CliRunner", cli: "Typer") -> None:
        result = cli_runner.invoke(cli, "server --help")

        assert result.exit_code == 0
        assert "Commands for Argilla server management" in result.stdout
