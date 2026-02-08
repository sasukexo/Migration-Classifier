from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile

from app.template_engine.record_builder import RecordBuilder
from app.template_engine.mapper import TemplateMapper
from app.template_engine.validator import TemplateValidator
from app.template_engine.generator import TemplateGenerator

router = APIRouter()


@router.post("/generate-mgn-template")
async def generate_template(
    file: UploadFile = File(...),
    account_id: str = Form(...),
    region: str = Form(...),
):

    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported.")

    # ⭐ STEP 1 — Extract
    records = RecordBuilder.build(file.file)

    mapper = TemplateMapper(account_id, region)
    validator = TemplateValidator()
    generator = TemplateGenerator()

    mapped = []
    mapping_failures = []

    # ⭐ STEP 2 — Transform
    for r in records:
        try:
            mapped.append(mapper.map_record(r))
        except Exception as e:
            r["mapping_error"] = str(e)
            mapping_failures.append(r)

    # ⭐ STEP 3 — Validate
    ready, failed = validator.validate(mapped)

    if not ready:
        raise HTTPException(400, "No valid servers found.")

    # ⭐ STEP 4 — Stream file safely
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    generator.write_ready_csv(ready, temp_file.name)

    return FileResponse(
        temp_file.name,
        media_type="text/csv",
        filename="mgn_import_ready.csv",
    )
