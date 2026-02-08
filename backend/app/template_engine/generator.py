# template_engine/generator.py

import csv
from typing import Iterable, Dict, Any


class TemplateGenerator:
    """
    Streams validated VM records directly into an AWS MGN-compatible CSV.

    Designed for large datasets:
        - Constant memory usage
        - No pandas dependency
        - Safe for 10k–100k servers
    """

    # Lock schema to prevent accidental column drift
    HEADERS = [
        "account-id",
        "region",
        "server:user-provided-id",
        "server:platform",
        "server:primary-ip",
    ]

    def write_csv(
        self,
        records: Iterable[Dict[str, Any]],
        output_path: str,
    ) -> None:
        """
        Streams records into a CSV file.

        Args:
            records: Iterable of VALIDATED records only
            output_path: Destination file path
        """

        with open(output_path, mode="w", newline="", encoding="utf-8") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.HEADERS,
                extrasaction="ignore",  # prevents crashes if extra keys exist
            )

            writer.writeheader()

            for record in records:
                self._validate_schema(record)
                writer.writerow(record)

    # ---------------------------------------
    # Optional: Write only READY records
    # ---------------------------------------

    def write_ready_csv(
        self,
        ready_records: Iterable[Dict[str, Any]],
        output_path: str = "mgn_import_ready.csv",
    ):
        self.write_csv(ready_records, output_path)

    # ---------------------------------------
    # Guardrail Against Schema Drift
    # ---------------------------------------

    def _validate_schema(self, record: Dict[str, Any]) -> None:
        """
        Prevent silent corruption if mapper changes.
        This is a VERY senior-level safety check.
        """

        missing = [h for h in self.HEADERS if h not in record]

        if missing:
            raise ValueError(
                f"Record missing required headers: {missing}"
            )
