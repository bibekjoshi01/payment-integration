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
        `http://localhost:8000/api/subscription-app/verify/${sessionId}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNTI3ODAyLCJpYXQiOjE3Mjk2NjM4MDIsImp0aSI6IjQxYWNmM2Q0ZDE5MzQzYzA4ZjQ4YTQ3NDdmMGY1MTZlIiwidXNlcl9pZCI6MX0.vsNeR82VsmXyAoAscawc9jnC64n2Xdd6KqPduVNk2es`,
          },
        }
      );

      if (response.ok) {
        const sessionDetails = await response.json();
        console.log("Session Details:", sessionDetails);
        setMessage("Payment Successfull!")
      } else {
        console.error("Failed to retrieve session details");
        setMessage("Payment Failed!")
      }
    } catch (error) {
      setMessage("Opps Something went wrong !")
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
