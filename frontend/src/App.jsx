// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import YantraDashboard from "./pages/YantraDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<YantraDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
