"""Tests for the CLI info command."""

from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from openmas import __version__
from openmas.cli.main import cli, version_callback


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_command_exists(self):
        """Test that the info command exists and is registered."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "info" in result.output

    def test_info_command_output(self):
        """Test that the info command outputs the correct information."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert f"OpenMAS version: {__version__}" in result.output
        assert "Python version:" in result.output
        assert "Platform:" in result.output
        # Check for new output format
        assert "Key Features & Integrations:" in result.output
        assert "Core Components:" in result.output
        assert "Available Communicators:" in result.output

    def test_info_command_communicators(self):
        """Test that the info command shows communicator information."""
        runner = CliRunner()
        
        # Mock the imports directly without using patch decorators
        mcp_mock = MagicMock(__version__="1.7.1")
        grpc_mock = MagicMock(__version__="1.71.0")
        paho_mqtt_mock = MagicMock(__version__="2.0.0")
        
        with patch.dict('sys.modules', {
            'mcp': mcp_mock,
            'grpc': grpc_mock,
            'paho': MagicMock(mqtt=paho_mqtt_mock)
        }):
            result = runner.invoke(cli, ["info"])
            
            # Verify the output contains communicator information
            assert result.exit_code == 0
            # Just check for basic protocol information
            assert "http" in result.output
            assert "MCP" in result.output
            assert "gRPC" in result.output
            assert "mqtt" in result.output
    
    def test_info_command_json_output(self):
        """Test that the info command outputs JSON when requested."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info", "--json"])
        assert result.exit_code == 0
        # JSON output should contain version but not the human-readable strings
        assert __version__ in result.output
        assert "OpenMAS version:" not in result.output
        # Check for communicators section in JSON
        assert "communicators" in result.output
        assert "versions" in result.output

    def test_version_flag(self):
        """Test that the --version flag shows the correct version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output
        # Should show the enhanced output
        assert "Key Features & Integrations:" in result.output
        assert "HTTP Communicator: Enabled" in result.output

    def test_version_callback_direct(self):
        """Test the version callback function directly."""
        # Create a mock context
        ctx = MagicMock()
        ctx.resilient_parsing = False
        
        # Set up the mocks
        mcp_mock = MagicMock(__version__="1.7.1")
        grpc_mock = MagicMock(__version__="1.71.0")
        paho_mqtt_mock = MagicMock(__version__="2.0.0")
        
        # Patch the import statements directly in version_callback's scope
        with patch.dict('sys.modules', {
            'mcp': mcp_mock,
            'grpc': grpc_mock,
            'paho': MagicMock(mqtt=paho_mqtt_mock)
        }):
            # Capture printed output
            with patch('click.echo') as mock_echo:
                version_callback(ctx, None, True)
                
                # Verify the correct output was generated
                mock_calls = mock_echo.call_args_list
                output_str = '\n'.join(c.args[0] for c in mock_calls)
                
                # Check for version information
                assert f"OpenMAS, version {__version__}" in output_str
                assert "HTTP Communicator: Enabled" in output_str
                assert "MCP (Model Context Protocol):" in output_str
                assert "gRPC:" in output_str
                assert "MQTT:" in output_str
