from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import csv

from app.template_engine.mapper import TemplateMapper
from app.template_engine.validator import TemplateValidator
from app.template_engine.generator import TemplateGenerator

router = APIRouter()


@router.post("/generate-mgn-template")
async def generate_template(
    file: UploadFile = File(...),
    account_id: str = Form(...),
    region: str = Form(...)
):

    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported.")

    mapper = TemplateMapper(account_id, region)
    validator = TemplateValidator()
    generator = TemplateGenerator()

    mapped_records = []
    mapping_failures = []

    # Read uploaded CSV
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()

    reader = csv.DictReader(decoded)

    for row in reader:
        vm = {
            "vm_name": row.get("VM Name"),
            "os": row.get("OS"),
            "ip": row.get("IP Address"),
        }

        try:
            mapped = mapper.map_record(vm)
            mapped_records.append(mapped)

        except Exception:
            mapping_failures.append(vm)

    ready, failed = validator.validate(mapped_records)

    if not ready:
        raise HTTPException(400, "No valid servers found.")

    # temp file prevents memory load
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    generator.write_ready_csv(ready, temp_file.name)

    return FileResponse(
        temp_file.name,
        media_type="text/csv",
        filename="mgn_import_ready.csv"
    )
