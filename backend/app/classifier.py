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

    # ORDER MATTERS (more specific first)

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
# VERSION EXTRACTION (SAFE)
# ------------------------------------------------
def extract_version(os_string):

    os_string = os_string.lower()

    # Remove architecture
    os_string = re.sub(r"\b(32|64)[-\s]?bit\b", "", os_string)

    # Remove brackets
    os_string = re.sub(r"\(.*?\)", "", os_string)

    # ⭐ HANDLE WINDOWS R2 FIRST
    if "r2" in os_string:

        year_match = re.search(r"20\d{2}", os_string)

        if year_match:
            return float(year_match.group()) + 0.1
            # Example:
            # 2008 -> 2008.1
            # So it becomes newer than base 2008

    # Normal extraction
    match = re.search(r"\b(20\d{2}|\d{1,2}\.\d+|\d{1,2})\b", os_string)

    if not match:
        return None

    return float(match.group())


# ------------------------------------------------
# VM IMPORT SUPPORT CHECK
# ------------------------------------------------

def vm_import_supported(family):

    windows = VMIE_RULES.get("windows", {})
    linux = VMIE_RULES.get("linux_families_supported", [])

    if family == "windows":
        return True

    if family in linux:
        return True

    return False

def extract_service_pack(os_string):

    match = re.search(r"sp\s?(\d+)", os_string.lower())

    if match:
        return int(match.group(1))

    return None

# ------------------------------------------------
# MAIN CLASSIFIER
# ------------------------------------------------
def classify_os(os_string):

    os_lower = os_string.lower()

    # HARD BLOCK
    if "32-bit" in os_lower and "windows" not in os_lower:
        return decision(
            "REBUILD_REQUIRED",
            "CRITICAL",
            "32-bit Linux is not supported by AWS MGN"
        )

    # Clean metadata
    os_lower = re.sub(r"\(.*?\)", "", os_lower)

    junk_phrases = ["or later", "datacenter", "standard", "enterprise"]

    for phrase in junk_phrases:
        os_lower = os_lower.replace(phrase, "")

    # Detect
    family = normalize_family(os_lower)
    version = extract_version(os_lower)

    # ✅ DEBUG — KEEP THIS HERE (inside function!)
    # print(f"DEBUG → OS={os_string} | family={family} | version={version}")

    # Unknown OS
    if not family:
        return decision(
            "NEEDS_REVIEW",
            "CRITICAL",
            "Unknown OS — manual validation required"
        )

    # Missing version
    if version is None:
        return decision(
            "ACTION_REQUIRED",
            "HIGH",
            "OS detected but version missing"
        )

    rules = MGN_RULES.get(family)
    # ------------------------------------------------
# ⭐ SPECIAL RULES (MUST RUN BEFORE ANYTHING ELSE)
# ------------------------------------------------

   # ------------------------------------------------
# SPECIAL RULES (HIGHEST PRIORITY)
# ------------------------------------------------

    special_rules = rules.get("special_rules", {})

    if version in special_rules:

        rule = special_rules[version]

        if "min_sp" in rule:

            sp = extract_service_pack(os_lower)

            # 🚨 SP missing → NEEDS REVIEW
            if sp is None:
                return decision(
                    "NEEDS_REVIEW",
                    "HIGH",
                    f"SLES {int(version)} requires SP{rule['min_sp']}+ — Service Pack not detected"
                )

            # 🚨 SP too low → NOT supported
            if sp < rule["min_sp"]:
                return decision(
                    "REBUILD_REQUIRED",
                    "CRITICAL",
                    f"SLES {int(version)} SP{sp} is not supported by AWS MGN"
                )

            # ✅ SP valid
            return decision(
                "MGN_SUPPORTED",
                "LOW",
                f"SLES {int(version)} SP{sp} supported by AWS MGN"
            )


    # ------------------------------------------------
    # WINDOWS
    # ------------------------------------------------

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
    if family == "sles" and version == 11:

        sp = extract_service_pack(os_lower)

        if sp is None:
            return decision(
                "ACTION_REQUIRED",
                "HIGH",
                "SLES 11 requires SP4+ — Service Pack not detected"
            )

        if sp < 4:
            return decision(
                "REBUILD_REQUIRED",
                "CRITICAL",
                f"SLES 11 SP{sp} is not supported by AWS MGN"
            )

        return decision(
            "MGN_SUPPORTED",
            "LOW",
            "SLES 11 SP4+ supported by AWS MGN"
        )
    # ------------------------------------------------
    # ⭐ LINUX (THIS IS THE BIG FIX)
    # ------------------------------------------------

    # ✅ FIRST — check minor ranges
    if "supported_minor_ranges" in rules:

        for low, high in rules["supported_minor_ranges"]:
            if low <= version <= high:
                return decision(
                    "MGN_SUPPORTED",
                    "LOW",
                    "Supported by AWS MGN"
                )

    # ✅ THEN check normal range
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

    # ------------------------------------------------
    # VM IMPORT
    # ------------------------------------------------

    if vm_import_supported(family):
        return decision(
            "VM_IMPORT_EXPORT",
            "HIGH",
            "Not supported by MGN — use VM Import/Export"
        )

    return decision(
        "NEEDS_REVIEW",
        "UNKNOWN",
        "Unable to determine migration path"
    )
    # ------------------------------------------------
# ⭐ SLES SPECIAL RULE (CRITICAL)
# ------------------------------------------------

    
