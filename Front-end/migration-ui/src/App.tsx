import { useState } from "react";
import Upload from "./components/Upload";
import Dashboard from "./components/Dashboard";
import VMTable from "./components/VMTable";
import MgnTemplateGenerator from "./components/MgnTemplateGenerator";
import { exportDashboard } from "./services/api";
import Footer from "./components/Footer";



function App() {

  const [view, setView] = useState<"classifier" | "template">("classifier");

  const [data, setData] = useState<any>(null);
  const [filteredVMs, setFilteredVMs] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null); // ⭐ CRITICAL

  const handleUpload = (response: any) => {
    setData(response);
    setFilteredVMs(response.data);
  };

  const filterVMs = (decision: string | null) => {

    if (!decision) {
      setFilteredVMs(data.data);
      return;
    }

    const filtered = data.data.filter(
      (vm: any) => vm.decision === decision
    );

    setFilteredVMs(filtered);
  };

  // ⭐ DOWNLOAD FUNCTION INSIDE COMPONENT (VERY IMPORTANT)
  const downloadDashboard = async () => {

    if (!selectedFile) {
      alert("Upload a CSV first.");
      return;
    }

    try {

      const blob = await exportDashboard(selectedFile);

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "migration_dashboard.xlsx";
      a.click();

    } catch (err) {
      console.error(err);
      alert("Failed to download report.");
    }
  };

  return (
    <div className="app-wrapper">

      {/* 🔥 TOP NAVBAR */}
      <div className="topbar">
        <div className="logo">Migration Platform</div>

        <div className="nav-right">
          <button onClick={() => setView("classifier")}>
            Classifier
          </button>

          <button onClick={() => setView("template")}>
            Template Generator
          </button>
        </div>
      </div>

      {/* 🔥 MAIN CONTENT */}
      <div className="app-container">

        {/* ✅ CLASSIFIER VIEW */}
        {view === "classifier" && (
          <>
            <h1 className="hero-title">
              Migration Readiness Dashboard
            </h1>

            <p className="hero-sub">
              Upload your vSphere export to instantly classify workloads for AWS migration.
            </p>

            {/* ⭐ PASS FILE SETTER */}
            <Upload 
              onUpload={handleUpload}
              setSelectedFile={setSelectedFile}
            />

            {data && (
              <>
                <Dashboard
                  summary={data.summary}
                  total={data.total}
                  onFilter={filterVMs}
                  onDownload={downloadDashboard} // ⭐ PASS DOWNLOAD
                />

                <VMTable data={filteredVMs} />
              </>
            )}
          </>
        )}

        {/* ✅ TEMPLATE GENERATOR VIEW */}
        {view === "template" && (
          <MgnTemplateGenerator />
        )}

      </div>
      <Footer />

    </div>
  );
}

export default App;
