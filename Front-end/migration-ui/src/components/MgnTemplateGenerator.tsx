import { useState } from "react";

const MgnTemplateGenerator = () => {

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [accountId, setAccountId] = useState("");
    const [region, setRegion] = useState("");
    const [loading, setLoading] = useState(false);

    const handleUpload = async () => {

        if (!selectedFile || !accountId || !region) {
            alert("Please fill all fields.");
            return;
        }

        setLoading(true);

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("account_id", accountId);
        formData.append("region", region);

        try {

            const response = await fetch(
                `orthodox-marie-jeanne-aswinxo-b6a366c1.koyeb.app`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error("Template generation failed");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "mgn_import_ready.csv";
            a.click();

        } catch (err) {
            console.error(err);
            alert("Server error.");
        }

        setLoading(false);
    };

    return (
        <div>

            <h2>MGN Template Generator</h2>

            <input
                type="file"
                accept=".csv"
                onChange={(e) =>
                    setSelectedFile(e.target.files?.[0] || null)
                }
            />

            <br /><br />

            <input
                placeholder="AWS Account ID"
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
            />

            <br /><br />

            <input
                placeholder="Region"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
            />

            <br /><br />

            <button onClick={handleUpload} disabled={loading}>
                {loading ? "Generating..." : "Generate Template"}
            </button>

        </div>
    );
};

export default MgnTemplateGenerator;
