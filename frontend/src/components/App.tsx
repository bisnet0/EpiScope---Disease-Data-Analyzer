import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { MainLayout } from "./Layout/MainLayout";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;