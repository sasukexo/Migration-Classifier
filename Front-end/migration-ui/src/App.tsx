import { useState } from "react";
import Upload from "./components/Upload";
import Dashboard from "./components/Dashboard";
import VMTable from "./components/VMTable";

function App() {

  const [data, setData] = useState<any>(null);
  const [filteredVMs, setFilteredVMs] = useState<any[]>([]);

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

  return (
    <>
      {/* 🔥 TOP NAVBAR */}
      <div className="topbar">
        <div className="logo">🚀 Migration Classifier</div>
        <div className="nav-right">AWS Migration Tool</div>
      </div>


      {/* 🔥 MAIN CONTENT */}
      <div className="app-container">

        {/* HERO */}
        <h1 className="hero-title">
          Migration Readiness Dashboard
        </h1>

        <p className="hero-sub">
          Upload your vSphere export to instantly classify workloads for AWS migration.
        </p>

        <Upload onUpload={handleUpload} />

        {data && (
          <>
            <Dashboard
              summary={data.summary}
              total={data.total}
              onFilter={filterVMs}
            />

            <VMTable data={filteredVMs} />
          </>
        )}

      </div>
    </>
  );
}

export default App;
