import { useState } from "react";
import { uploadCSV } from "../services/api";

interface Props {
  onUpload: (data: any) => void;
}

export default function Upload({ onUpload }: Props) {
  const [loading, setLoading] = useState(false);

  const handleFile = async (e: any) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);

    try {
      const data = await uploadCSV(file);
      onUpload(data);
    } catch (err) {
      alert("Upload failed");
    }

    setLoading(false);
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <input type="file" accept=".csv" onChange={handleFile} />
      {loading && <p>Classifying VMs...</p>}
    </div>
  );
}
