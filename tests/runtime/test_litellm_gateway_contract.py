import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class LiteLlmGatewayContractTests(unittest.TestCase):
    def test_gateway_management_script_keeps_runtime_local_and_loopback(self) -> None:
        script = (ROOT / "scripts" / "Manage-LiteLLMGateway.ps1").read_text(encoding="utf-8")

        self.assertIn('.runtime\\litellm', script)
        self.assertIn('[ValidateSet("Install", "RenderConfig", "Start", "Stop", "Status", "Smoke", "CockpitStatus", "PrepareCockpitUpstream", "WriteCodexProfile", "Rollback", "All")]', script)
        self.assertIn('[string]$HostName = "127.0.0.1"', script)
        self.assertIn('[string]$UpstreamModel = "gpt-5.5"', script)
        self.assertIn('api_base: http://127.0.0.1:$CockpitPort/v1', script)
        self.assertIn('api_key: $cockpitApiKey', script)
        self.assertIn('master_key: $masterKey', script)
        self.assertIn("ConvertTo-YamlSingleQuoted", script)
        self.assertIn('$values["LITELLM_MASTER_KEY"] = $cockpit.api_key', script)
        self.assertIn('if (`$name -eq "LITELLM_MASTER_KEY") { continue }', script)
        self.assertIn('[Environment]::SetEnvironmentVariable("LITELLM_MASTER_KEY", `$null, "Process")', script)
        self.assertIn("Get-ChildProcessIds", script)
        self.assertIn("Get-LiteLlmPortOwnerIds", script)
        self.assertIn("--telemetry False", script)
        self.assertNotIn("--telemetry False --local", script)
        self.assertIn("secret_redacted", script)
        self.assertNotIn("0.0.0.0", script)

    def test_cockpit_upstream_uses_current_account_and_allows_local_account_classes(self) -> None:
        script = (ROOT / "scripts" / "Manage-LiteLLMGateway.ps1").read_text(encoding="utf-8")

        self.assertIn("governed-cockpit-api-$CockpitPort-block-inbound", script)
        self.assertIn("New-NetFirewallRule", script)
        self.assertIn("netsh advfirewall show allprofiles firewallpolicy", script)
        self.assertIn("BlockInbound,AllowOutbound", script)
        self.assertIn('-Direction Inbound -Action Block -Protocol TCP -LocalPort $CockpitPort', script)
        self.assertIn('"PrepareCockpitUpstream"', script)
        self.assertIn("Get-CockpitCurrentAccountForUpstream", script)
        self.assertIn("current_codex_account_not_found", script)
        self.assertNotIn("current_account_is_api_key_account", script)
        self.assertNotIn("current_account_is_free_account", script)
        self.assertIn('$json.restrictFreeAccounts = $false', script)
        self.assertIn('$json.followCurrentAccount = $true', script)
        self.assertIn('$json.accountIds = @($current.id)', script)
        self.assertIn("Ensure-CockpitLaunchBindingForGateway", script)
        self.assertIn("followLocalAccount", script)
        self.assertIn("cleared_fixed_codex_instance_binding", script)
        self.assertNotIn("Get-CockpitEligibleAccountIds", script)
        self.assertIn("firewall_block_present", script)
        self.assertIn("firewall_profile_default_block", script)
        self.assertIn("safe_for_upstream", script)

    def test_codex_profile_activates_gateway_and_uses_non_builtin_provider(self) -> None:
        script = (ROOT / "scripts" / "Manage-LiteLLMGateway.ps1").read_text(encoding="utf-8")

        self.assertIn("[profiles.litellm-gateway]", script)
        self.assertIn('model_provider = "litellm_gateway"', script)
        self.assertIn('Set-TomlTopLevelString -Text $text -Name "model" -Value $ModelAlias', script)
        self.assertIn('Set-TomlTopLevelString -Text $text -Name "forced_login_method" -Value "api"', script)
        self.assertIn('Set-TomlTopLevelString -Text $text -Name "model_provider" -Value "litellm_gateway"', script)
        self.assertIn("[model_providers.litellm_gateway]", script)
        self.assertIn('base_url = "http://127.0.0.1:$Port/v1"', script)
        self.assertIn('env_key = "LITELLM_MASTER_KEY"', script)
        self.assertIn('supports_websockets = false', script)
        self.assertIn('auth_mode = "apikey"', script)
        self.assertIn('source = "governed-litellm-gateway"', script)
        self.assertIn('default_provider_changed = $true', script)
        self.assertIn('auth_written = $true', script)
        self.assertNotIn("[model_providers.openai]", script)

    def test_runbook_documents_safety_boundary_and_rollback(self) -> None:
        runbook = (ROOT / "docs" / "runbooks" / "litellm-cockpit-gateway.md").read_text(encoding="utf-8")

        self.assertIn("Codex -> LiteLLM -> Cockpit API service", runbook)
        self.assertIn("Cockpit Tools remains the owner", runbook)
        self.assertIn("selectable mode, not a replacement for the old direct Codex App/CLI OAuth/API projection", runbook)
        self.assertIn("CodexGatewayEnable", runbook)
        self.assertIn("CodexGatewayRollback", runbook)
        self.assertIn("CodexApiProjectionRepair", runbook)
        self.assertIn("CodexOauthProjectionRepair", runbook)
        self.assertIn("LiteLLM binds to `127.0.0.1:4000` by default", runbook)
        self.assertIn("activates `model_provider = \"litellm_gateway\"`", runbook)
        self.assertIn("Codex App is not restarted by this lane", runbook)
        self.assertIn("Rollback stops only the PID", runbook)


if __name__ == "__main__":
    unittest.main()
