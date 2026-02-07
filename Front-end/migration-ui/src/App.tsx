import { useState } from "react";
import Upload from "./components/Upload";
import Dashboard from "./components/Dashboard";
import VMTable from "./components/VMTable";

function App() {

  // ALL response data
  const [data, setData] = useState<any>(null);

  // Filtered VMs shown in table
  const [filteredVMs, setFilteredVMs] = useState<any[]>([]);


  // Called after CSV upload
  const handleUpload = (response: any) => {
    setData(response);
    setFilteredVMs(response.data); // show all initially
  };


  // Filter when dashboard card clicked
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
    <div
      style={{
        padding: 40,
        background: "#f7f9fc",
        minHeight: "100vh",
        fontFamily: "Inter, sans-serif"
      }}
    >
      <h1 style={{ marginBottom: 30 }}>
        🚀 Migration Classifier Dashboard
      </h1>

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
  );
}

export default App;
