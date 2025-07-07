import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import YantraDashboard from "./pages/YantraDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<YantraDashboard />} />
        {/* You can add more routes here later */}
      </Routes>
    </Router>
  );
}

export default App;
