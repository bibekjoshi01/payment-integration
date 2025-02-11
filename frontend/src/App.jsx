import "./App.css";
import "react-toastify/dist/ReactToastify.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";

import PayStack from "./pages/PayStack";
import PayStackPaymentCallback from "./pages/PayStackPaymentCallback";

const App = () => {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/paystack" element={<PayStack />} />
          <Route
            path="/paystack-callback"
            element={<PayStackPaymentCallback />}
          />
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </>
  );
};

export default App;
