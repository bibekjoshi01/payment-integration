import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const SuccessPage = () => {
  const location = useLocation();
  const [message, setMessage] = useState();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sessionId = params.get("session_id");

    if (sessionId) {
      // Call a function to retrieve the session details
      retrieveStripeSession(sessionId);
    }
  }, [location]);

  const retrieveStripeSession = async (sessionId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/public/subscription-app/subscription/${sessionId}/capture`,
        {
          method: "POST",
          body: JSON.stringify({
            paymentMethod: "STRIPE",
          }),
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNDUyNjMxLCJpYXQiOjE3Mjk4NDc4MzEsImp0aSI6ImQ5Y2Q4M2FhODdlMTQ3MTQ5ODlmZGM4ODk5NDczMTk3IiwidXNlcl9pZCI6M30._kRS0eq1KBEEOnf8NaK1aULGLnY4AImCiulfaCr11Yg`,
          },
        }
      );

      if (response.ok) {
        const sessionDetails = await response.json();
        console.log("Session Details:", sessionDetails);
        setMessage("Payment Successfull!");
      } else {
        console.error("Failed to retrieve session details");
        setMessage("Payment Failed!");
      }
    } catch (error) {
      setMessage("Opps Something went wrong !");
      console.error("Error fetching session details:", error);
    }
  };

  return (
    <div>
      <h1>{message}</h1>
      <p>Your payment has been processed successfully.</p>
    </div>
  );
};

export default SuccessPage;
