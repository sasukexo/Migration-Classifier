interface Props {
  summary: Record<string, number>;
  total: number;
  onFilter: (decision: string | null) => void;
  onDownload: () => void;
}

export default function Dashboard({
  summary,
  total,
  onFilter,
  onDownload,
}: Props) {
  return (
    <>
      {/* DOWNLOAD BUTTON */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: "20px",
        }}
      >
        <button onClick={onDownload} style={styles.downloadBtn}>
          ⬇ Download Migration Report
        </button>
      </div>

      <div style={styles.grid}>
        <Card
          title="TOTAL"
          value={total}
          onClick={() => onFilter(null)}
          color="#444"
        />

        {Object.entries(summary).map(([key, value]) => (
          <Card
            key={key}
            title={key}
            value={value}
            onClick={() => onFilter(key)}
            color={getColor(key)}
          />
        ))}
      </div>
    </>
  );
}

function Card({ title, value, onClick, color }: any) {
  return (
    <div
      onClick={onClick}
      style={{ ...styles.card, borderTop: `6px solid ${color}` }}
    >
      <h4>{title}</h4>
      <h1>{value}</h1>
    </div>
  );
}

const styles = {
  grid: {
    display: "flex",
    gap: "20px",
    marginBottom: "30px",
    flexWrap: "wrap",
  },
  card: {
    cursor: "pointer",
    padding: "20px",
    minWidth: "150px",
    borderRadius: "12px",
    background: "white",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  },
  downloadBtn: {
    padding: "12px 20px",
    borderRadius: "10px",
    border: "none",
    background: "#635bff",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
  },
};

function getColor(decision: string) {
  if (decision.includes("MGN")) return "#4CAF50";
  if (decision.includes("IMPORT")) return "#FF9800";
  if (decision.includes("ACTION")) return "#F44336";
  if (decision.includes("REBUILD")) return "#9C27B0";

  return "#607D8B";
}
