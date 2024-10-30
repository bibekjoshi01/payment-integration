import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { createBrowserRouter } from "react-router-dom";
import { RouterProvider } from "react-router-dom";
import SuccessPage from "./pages/StripeSuccess.jsx";
import StripeSubscription from "./components/Stripe/Subscription.jsx";
import StripeCheckOut from "./components/Stripe/Stripe";
import Flutterwave from "./components/Stripe/flutterwave.jsx";
import Donate from "./components/Donate/Donate.jsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/subscription",
    element: <StripeSubscription />,
  },
  {
    path: "/stripe",
    element: <StripeCheckOut />,
  },
  {
    path: "/donate",
    element: <Donate />,
  },
  { path: "/payment-success", element: <SuccessPage /> },
  { path: "/flutterwave", element: <Flutterwave /> },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
