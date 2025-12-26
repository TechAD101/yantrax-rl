// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import YantraDashboard from "./pages/YantraDashboard";
import Journal from "./pages/Journal";
import Onboarding from "./pages/Onboarding";
import Moodboard from "./pages/Moodboard";
import Settings from "./pages/Settings";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<YantraDashboard />} />
        <Route path="/journal" element={<Journal />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/moodboard" element={<Moodboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<YantraDashboard />} />
      </Routes>
    </Router>
  );
}

export default () => <ErrorBoundary><App /></ErrorBoundary>
