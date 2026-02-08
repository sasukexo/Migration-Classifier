# template_engine/mapper.py

from typing import Dict, Any
import re


class TemplateMapper:
    """
    Maps normalized VM records into AWS MGN import template format.
    """

    def __init__(self, account_id: str, region: str):
        self.account_id = account_id
        self.region = region

    # -----------------------------
    # Public API
    # -----------------------------

    def map_record(self, vm: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a VM dictionary into an MGN-ready row.
        Assumes input is already normalized.
        """

        platform = self._derive_platform(vm.get("os", ""))

        return {
            "account-id": self.account_id,
            "region": self.region,
            "server:user-provided-id": vm.get("vm_name"),
            "server:platform": platform,
            "server:primary-ip": self._extract_ipv4(vm.get("ip")),
        }

    # -----------------------------
    # Platform Detection
    # -----------------------------

    def _derive_platform(self, os_string: str) -> str:
        """
        Convert OS string → linux/windows
        Raise error if unknown to prevent bad imports.
        """

        os_lower = os_string.lower()

        if "windows" in os_lower:
            return "WINDOWS"

        linux_indicators = [
            "linux",
            "rhel",
            "red hat",
            "centos",
            "ubuntu",
            "debian",
            "oracle",
            "suse",
            "sles",
            "amazon linux",
        ]

        if any(keyword in os_lower for keyword in linux_indicators):
            return "LINUX"

        raise ValueError(f"Unknown OS platform: {os_string}")

    # -----------------------------
    # IPv4 Extraction
    # -----------------------------

    def _extract_ipv4(self, ip_field: str) -> str | None:
        """
        Extract first valid IPv4 from a messy field.
        Ignores IPv6 automatically.
        """

        if not ip_field:
            return None

        ipv4_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        matches = re.findall(ipv4_pattern, ip_field)

        return matches[0] if matches else None
