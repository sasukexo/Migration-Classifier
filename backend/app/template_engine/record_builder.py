import pandas as pd
from fastapi import HTTPException


class RecordBuilder:

    COLUMN_ALIASES = {
        "vm_name": ["vm name", "name", "guest name"],
        "os": ["os", "guest os", "operating system"],
        "ip": ["ip", "ip address", "primary ip"],
    }

    @classmethod
    def build(cls, file):

        df = pd.read_csv(file)

        # remove ghost excel rows
        df = df.dropna(how="all")

        # normalize headers
        df.columns = df.columns.str.strip().str.lower()

        column_map = cls.resolve_columns(df)

        records = []

        for _, row in df.iterrows():

            records.append({
                "vm_name": row[column_map["vm_name"]],
                "os": row[column_map["os"]],
                "ip": row[column_map["ip"]],
            })

        return records

    # ------------------------

    @classmethod
    def resolve_columns(cls, df):

        mapping = {}

        for canonical, aliases in cls.COLUMN_ALIASES.items():

            match = next(
                (col for col in df.columns if col in aliases),
                None
            )

            if not match:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required column for '{canonical}'. "
                           f"Accepted names: {aliases}"
                )

            mapping[canonical] = match

        return mapping
