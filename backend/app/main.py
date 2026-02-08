from fastapi import FastAPI, UploadFile, File
import pandas as pd
from app.classifier import classify_os
from fastapi.middleware.cors import CORSMiddleware
from app.api.template_routes import router as template_router
from app.api.classifier_routes import router as classifier_router





# ✅ CREATE APP FIRST
app = FastAPI()


# ✅ ADD MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for internal tools
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ INCLUDE ROUTERS AFTER APP EXISTS
app.include_router(template_router, prefix="/template")
app.include_router(classifier_router, prefix="/classifier")


@app.post("/classify")
async def classify(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    results = []

    for _, row in df.iterrows():

        os_value = str(row.get("Guest OS", ""))

        classification = classify_os(os_value)

        results.append({
            "VM Name": row.get("Name"),
            "OS": os_value,
            "CPU": row.get("CPU"),
            "RAM": row.get("RAM"),
            "Power State": row.get("Power State"),
            **classification
        })

    result_df = pd.DataFrame(results)

    summary = result_df["decision"].value_counts().to_dict()

    return {
        "summary": summary,
        "total": len(result_df),
        "data": results
    }
