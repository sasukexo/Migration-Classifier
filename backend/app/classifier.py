import re
from app.rules_loader import load_rules


# ------------------------------------------------
# LOAD RULES
# ------------------------------------------------

MGN_RULES = load_rules("rules/mgn_rules.yaml")
VMIE_RULES = load_rules("rules/vmie_rules.yaml")


# ------------------------------------------------
# DECISION HELPERS
# ------------------------------------------------

def strategy_map(decision):
    return {
        "MGN_SUPPORTED": "REHOST",
        "MGN_SUPPORTED_WITH_CONDITION": "REHOST_WITH_UPGRADE",
        "VM_IMPORT_EXPORT": "LEGACY_REHOST",
        "ACTION_REQUIRED": "MANUAL_VALIDATION",
        "NEEDS_REVIEW": "MANUAL_CHECK",
        "REBUILD_REQUIRED": "REPLATFORM"
    }[decision]


def decision(type, risk, reason):
    return {
        "decision": type,
        "strategy": strategy_map(type),
        "risk": risk,
        "reason": reason
    }


# ------------------------------------------------
# NORMALIZE OS FAMILY
# ------------------------------------------------

def normalize_family(os_string: str):

    os_string = os_string.lower()

    if "red hat" in os_string or "rhel" in os_string:
        return "rhel"

    if "centos" in os_string:
        return "centos"

    if "oracle" in os_string:
        return "oracle"

    if "rocky" in os_string:
        return "rocky"

    if "amazon linux" in os_string:
        return "amazon"

    if "suse" in os_string:
        return "sles"

    if "ubuntu" in os_string:
        return "ubuntu"

    if "debian" in os_string:
        return "debian"

    if "windows" in os_string:
        return "windows"

    return None


# ------------------------------------------------
# VERSION EXTRACTION (SAFE + NORMALIZED)
# ------------------------------------------------

def extract_version(os_string):

    os_string = os_string.lower()

    # Remove architecture
    os_string = re.sub(r"\b(32|64)[-\s]?bit\b", "", os_string)

    # Remove brackets
    os_string = re.sub(r"\(.*?\)", "", os_string)

    # ⭐ Handle Windows R2
    if "r2" in os_string:
        year_match = re.search(r"20\d{2}", os_string)
        if year_match:
            return int(year_match.group()) + 1  # treat R2 as newer

    match = re.search(r"\b(20\d{2}|\d{1,2}\.\d+|\d{1,2})\b", os_string)

    if not match:
        return None

    return int(float(match.group()))  # normalize ALWAYS


# ------------------------------------------------
# SERVICE PACK EXTRACTION
# ------------------------------------------------

def extract_service_pack(os_string):

    match = re.search(r"sp\s?(\d+)", os_string.lower())

    if match:
        return int(match.group(1))

    return None


# ------------------------------------------------
# VM IMPORT SUPPORT CHECK
# ------------------------------------------------

def vm_import_supported(family):

    if family == "windows":
        return True

    return family in VMIE_RULES.get("linux_families_supported", [])


# ------------------------------------------------
# MAIN CLASSIFIER
# ------------------------------------------------

def classify_os(os_string):

    os_lower = os_string.lower()

    # ------------------------------------------------
    # HARD BLOCK — 32bit Linux
    # ------------------------------------------------

    if "32-bit" in os_lower and "windows" not in os_lower:
        return decision(
            "REBUILD_REQUIRED",
            "CRITICAL",
            "32-bit Linux is not supported by AWS MGN"
        )

    # Clean metadata
    os_lower = re.sub(r"\(.*?\)", "", os_lower)

    junk = ["or later", "datacenter", "standard", "enterprise"]

    for j in junk:
        os_lower = os_lower.replace(j, "")

    # ------------------------------------------------
    # DETECT FAMILY + VERSION
    # ------------------------------------------------

    family = normalize_family(os_lower)
    version = extract_version(os_lower)

    if not family:
        return decision(
            "NEEDS_REVIEW",
            "CRITICAL",
            "Unknown OS — manual validation required"
        )

    if version is None:
        return decision(
            "ACTION_REQUIRED",
            "HIGH",
            "OS detected but version missing"
        )

    rules = MGN_RULES.get(family)

    if not rules:
        return decision(
            "NEEDS_REVIEW",
            "HIGH",
            "No MGN rules found for this OS"
        )

    # ====================================================
    # ⭐⭐⭐ SPECIAL RULES — HIGHEST PRIORITY
    # ====================================================

    special_rules = rules.get("special_rules", {})
    version_key = int(version)

    if version_key in special_rules:

        rule = special_rules[version_key]

        if "min_sp" in rule:

            sp = extract_service_pack(os_lower)

            # Missing SP → NEEDS REVIEW
            if sp is None:
                return decision(
                    "NEEDS_REVIEW",
                    "HIGH",
                    f"{family.upper()} {version} requires SP{rule['min_sp']}+ — Service Pack not detected"
                )

            # SP too low → rebuild
            if sp < rule["min_sp"]:
                return decision(
                    "REBUILD_REQUIRED",
                    "CRITICAL",
                    f"{family.upper()} {version} SP{sp} is not supported by AWS MGN"
                )

            # Valid SP
            return decision(
                "MGN_SUPPORTED",
                "LOW",
                f"{family.upper()} {version} SP{sp} supported by AWS MGN"
            )

    # ====================================================
    # WINDOWS LOGIC
    # ====================================================

    if family == "windows":

        is_server = "server" in os_lower or version >= 2000

        if is_server:

            low, high = rules["server_supported_range"]

            if low <= version <= high:
                return decision(
                    "MGN_SUPPORTED",
                    "LOW",
                    "Supported Windows Server"
                )

        else:

            if version in rules.get("client_supported", []):
                return decision(
                    "MGN_SUPPORTED",
                    "LOW",
                    "Supported Windows Client"
                )

        if version in rules.get("conditional", []):
            return decision(
                "MGN_SUPPORTED_WITH_CONDITION",
                "MEDIUM",
                "Older Windows — upgrade recommended"
            )

        return decision(
            "VM_IMPORT_EXPORT",
            "HIGH",
            "Not supported by MGN — use VM Import/Export"
        )

    # ====================================================
    # LINUX SUPPORT — MINOR RANGES FIRST
    # ====================================================

    if "supported_minor_ranges" in rules:

        for low, high in rules["supported_minor_ranges"]:
            if low <= version <= high:
                return decision(
                    "MGN_SUPPORTED",
                    "LOW",
                    "Supported by AWS MGN"
                )

    # Standard range
    if "supported_range" in rules:

        low, high = rules["supported_range"]

        if low <= version <= high:
            return decision(
                "MGN_SUPPORTED",
                "LOW",
                "Supported by AWS MGN"
            )

    # Conditional
    if version in rules.get("conditional", []):
        return decision(
            "MGN_SUPPORTED_WITH_CONDITION",
            "MEDIUM",
            "Supported but nearing deprecation"
        )

    # ====================================================
    # VM IMPORT FALLBACK
    # ====================================================

    if vm_import_supported(family):
        return decision(
            "VM_IMPORT_EXPORT",
            "HIGH",
            "Not supported by MGN — use VM Import/Export"
        )

    # Final safety
    return decision(
        "NEEDS_REVIEW",
        "UNKNOWN",
        "Unable to determine migration path"
    )
