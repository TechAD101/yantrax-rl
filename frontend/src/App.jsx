// src/App.jsx
import React, { Suspense } from "react";
import ErrorBoundary from "./components/ErrorBoundary";
import { Routes, Route, Navigate } from "react-router-dom";

const YantraDashboard = React.lazy(() => import("./pages/YantraDashboard"));
const Journal = React.lazy(() => import("./pages/Journal"));
const Onboarding = React.lazy(() => import("./pages/Onboarding"));
const Moodboard = React.lazy(() => import("./pages/Moodboard"));
const Settings = React.lazy(() => import("./pages/Settings"));

function App() {
  return (
      <ErrorBoundary>
        <Suspense fallback={<div style={{padding:20,color:'#fff'}}>Loading…</div>}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<YantraDashboard />} />
            <Route path="/journal" element={<Journal />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/moodboard" element={<Moodboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<YantraDashboard />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
  );
}

export default App