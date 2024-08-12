import React from "react";
import ReactDOM from "react-dom/client";
import PayPal from "./PayPal.tsx";
import Flutterwaze from "./Flutterwaze.tsx";
import Stripe from "./Stripe.tsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <PayPal />
    <Flutterwaze />
    <Stripe />
  </React.StrictMode>
);
