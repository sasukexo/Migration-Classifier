from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from app.classifier import classify_os

router = APIRouter()


@router.post("/export-dashboard")
async def export_dashboard(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    results = []

    for _, row in df.iterrows():

        classification = classify_os(str(row.get("Guest OS", "")))

        results.append({
            "VM Name": row.get("Name"),
            "OS": row.get("Guest OS"),
            **classification
        })

    result_df = pd.DataFrame(results)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        for decision, data in result_df.groupby("decision"):
            data.to_excel(writer, sheet_name=decision[:31], index=False)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=migration_dashboard.xlsx"
        }
    )
