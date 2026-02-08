import { useState } from "react";
import Upload from "./components/Upload";
import Dashboard from "./components/Dashboard";
import VMTable from "./components/VMTable";
import MgnTemplateGenerator from "./components/MgnTemplateGenerator";
import Sidebar from "./components/sidebar";   // ✅ FIXED
import Footer from "./components/footer";     // ✅ FIXED
import { exportDashboard } from "./services/api";

function App() {

  const [view, setView] = useState<"classifier" | "template">("classifier");

  const [data, setData] = useState<any>(null);
  const [filteredVMs, setFilteredVMs] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

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

    } catch {
      alert("Failed to download report.");
    }
  };

  return (
   <div className="app-shell">

      {/* Sidebar */}
      <Sidebar view={view} setView={setView} />

      {/* Main Area */}
      <div className="main-area">

        <div className="app-container">

          {view === "classifier" && (
            <>
              <h1 className="hero-title">
                Migration Readiness Dashboard
              </h1>

              <p className="hero-sub">
                Upload your vSphere export to instantly classify workloads for AWS migration.
              </p>

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
                    onDownload={downloadDashboard}
                  />

                  <VMTable data={filteredVMs} />
                </>
              )}
            </>
          )}

          {view === "template" && (
            <MgnTemplateGenerator />
          )}

        </div>

        <Footer />

      </div>
    </div>
  );
}

export default App;