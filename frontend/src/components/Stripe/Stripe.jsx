import axios from "axios";
import "./Subscription.css";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";

function StripeCheckOut() {
  const stripePromise = loadStripe(
    "pk_test_51QD0OqRwgyy5ljInlrYOZ55FKPnQBJmqOHLtkT3Ew0O67BpYiwMmBY9shoYbgYEMkIIeeiFUieBx7VybFchbfEGn00wjbXU07T"
  );

  const handleSubscribe = () => {
    axios
      .post(
        "http://localhost:8000/api/v1/public/order-app/orders",
        {
          orderType: "PRINT",
          orderNo: "string",
          customer: 3,
          deliveryCharge: "100.00",
          grandTotal: "200.00",
          paymentMethod: "STRIPE",
          note: "string",
          orderDetails: [
            {
              magazineLang: "ENGLISH",
              magazine: "d986780c-4a6f-495a-80e1-bb82a628e2dd",
              price: "100.00",
              qty: 1,
              netAmount: "100.00",
            },
          ],
          orderAddresses: [
            {
              fullName: "string",
              email: "user@example.com",
              phoneNo: "string",
              countrySubdivision: "5f059d58-db65-4b79-baea-ccaa4cc6a22d",
              city: "string",
              streetAddress: "string",
              nearestLandmark: "string",
              postalCode: "string",
              isBillingAddress: true,
              isShippingAddress: true,
            },
          ],
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDUyNjMxLCJpYXQiOjE3Mjk4NDc4MzEsImp0aSI6ImQ5Y2Q4M2FhODdlMTQ3MTQ5ODlmZGM4ODk5NDczMTk3IiwidXNlcl9pZCI6M30._kRS0eq1KBEEOnf8NaK1aULGLnY4AImCiulfaCr11Yg`,
          },
        }
      )
      .then((response) => {
        const sessionId = response?.data?.sessionId;
        console.log(sessionId, "response");

        // Redirect to Stripe Checkout page
        stripePromise.then((stripe) => {
          stripe.redirectToCheckout({ sessionId });
        });
      })
      .catch((error) => {
        console.error("Error creating subscription", error);
      });
  };

  return (
    <Elements stripe={stripePromise}>
      <button onClick={() => handleSubscribe()}>Checkout</button>
    </Elements>
  );
}

export default StripeCheckOut;
