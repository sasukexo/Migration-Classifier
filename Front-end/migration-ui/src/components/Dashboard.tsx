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
      <div style={{
        display: "flex",
        justifyContent: "flex-end",
        marginBottom: "20px",
      }}>
        <button onClick={onDownload}>
          ⬇ Download Migration Report
        </button>
      </div>

      <div style={styles.grid}>
        <Card
          title="TOTAL"
          value={total}
          onClick={() => onFilter(null)}
          color="#64748b"
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
      style={{
        ...styles.card,
        borderTop: `6px solid ${color}`,
        background: "var(--card-bg)",
        color: "var(--text-main)"
      }}
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
    padding: "24px",
    minWidth: "180px",
    borderRadius: "14px",
    boxShadow: "var(--shadow)",
    transition: "0.2s"
  },
};

function getColor(decision: string) {
  if (decision.includes("MGN")) return "#22c55e";
  if (decision.includes("IMPORT")) return "#f59e0b";
  if (decision.includes("ACTION")) return "#ef4444";
  if (decision.includes("REBUILD")) return "#a855f7";

  return "#64748b";
}
