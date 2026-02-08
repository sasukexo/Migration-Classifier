# template_engine/validator.py

from typing import List, Dict, Any, Tuple


class TemplateValidator:
    """
    Validates mapped VM records before template generation.
    Separates READY vs FAILED records.
    """

    REQUIRED_FIELDS = [
        "server:user-provided-id",
        "server:platform",
        "server:primary-ip",
    ]

    # -----------------------------
    # Public API
    # -----------------------------

    def validate(
        self, records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Returns:
            ready_records
            failed_records (with reasons)
        """

        ready = []
        failed = []

        seen_ips = set()
        seen_names = set()

        for record in records:
            errors = self._validate_record(record, seen_ips, seen_names)

            if errors:
                record["validation_errors"] = errors
                failed.append(record)
            else:
                ready.append(record)

        return ready, failed

    # -----------------------------
    # Record Validation
    # -----------------------------

    def _validate_record(
        self,
        record: Dict[str, Any],
        seen_ips: set,
        seen_names: set,
    ) -> List[str]:

        errors = []

        # Required fields
        for field in self.REQUIRED_FIELDS:
            if not record.get(field):
                errors.append(f"Missing required field: {field}")

        name = record.get("server:user-provided-id")
        ip = record.get("server:primary-ip")

        # Duplicate name
        if name:
            if name in seen_names:
                errors.append("Duplicate VM name detected")
            else:
                seen_names.add(name)

        # Duplicate IP
        if ip:
            if ip in seen_ips:
                errors.append("Duplicate IP detected")
            else:
                seen_ips.add(ip)

        return errors
