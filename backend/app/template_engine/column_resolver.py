from fastapi import HTTPException


class ColumnResolver:
    """
    Resolves flexible CSV column names.
    Ignores everything except required columns.
    """

    COLUMN_ALIASES = {
        "vm_name": [
            "vm name",
            "name",
            "guest name",
            "virtual machine",
        ],
        "os": [
            "os",
            "guest os",
            "operating system",
        ],
        "ip": [
            "ip",
            "ip address",
            "primary ip",
        ],
    }

    @classmethod
    def normalize_columns(cls, df):
        """
        Lowercase + trim whitespace.
        Prevents hidden CSV bugs.
        """
        df.columns = df.columns.str.strip().str.lower()
        return df

    @classmethod
    def resolve(cls, df):
        """
        Returns mapping:
        canonical → actual column
        """

        df = cls.normalize_columns(df)

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
