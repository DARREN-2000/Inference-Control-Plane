import { BrowserRouter, Routes, Route } from "react-router";
import { MainLayout } from "./layouts/MainLayout";
import Home from "./pages/Home";

function App() {
  return (
    <BrowserRouter basename="/Inference-Control-Plane">
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="*" element={<Home />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
