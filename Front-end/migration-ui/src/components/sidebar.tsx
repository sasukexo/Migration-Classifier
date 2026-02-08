import { useEffect, useState } from "react";

interface Props {
  view: "classifier" | "template";
  setView: (view: "classifier" | "template") => void;
}

export default function Sidebar({ view, setView }: Props) {

  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <div className="sidebar">

      <div className="sidebar-logo">
         Migration Platform
      </div>

      <nav className="sidebar-nav">

        <button
          className={view === "classifier" ? "nav-item active" : "nav-item"}
          onClick={() => setView("classifier")}
        >
          Classifier
        </button>

        <button
          className={view === "template" ? "nav-item active" : "nav-item"}
          onClick={() => setView("template")}
        >
           Template Generator
        </button>

      </nav>

      {/* Push toggle to bottom */}
      <div style={{ marginTop: "auto" }}>
        <button onClick={toggleTheme} className="nav-item">
          {theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

    </div>
  );
}
