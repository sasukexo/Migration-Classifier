export default function Footer() {
  return (
    <footer style={styles.footer}>
      Made with <span style={{ color: "#ff4d6d" }}>❤️</span>
 by <strong>Aswin</strong>
    </footer>
  );
}

const styles = {
  footer: {
    marginTop: "60px",
    padding: "20px",
    textAlign: "center" as const,
    color: "#666",
    fontSize: "14px",
    borderTop: "1px solid #eee",
  },
};
