import "./App.css";
import "react-toastify/dist/ReactToastify.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import { GoogleOAuthProvider } from "@react-oauth/google";

import PayStack from "./pages/PayStack";
import PayStackPaymentCallback from "./pages/PayStackPaymentCallback";
import GoogleAuth from "./pages/GoogleAuth";

const App = () => {
  return (
    <GoogleOAuthProvider clientId="">
      <BrowserRouter>
        <Routes>
          <Route path="/paystack" element={<PayStack />} />
          <Route
            path="/paystack-callback"
            element={<PayStackPaymentCallback />}
          />
          <Route path="/" element={<GoogleAuth />} />
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </GoogleOAuthProvider>
  );
};

export default App;
