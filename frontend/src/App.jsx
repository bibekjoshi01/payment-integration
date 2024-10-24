import axios from "axios";
import "./App.css";
import { useEffect, useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSubscriptionPlans = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/subscription-app/subscription-plans"
        );
        setData(response.data.results); 
      } catch (error) {
        console.error("Error fetching subscription plans:", error);
      }
    };

    fetchSubscriptionPlans();
  }, []);

  const stripePromise = loadStripe(
    "pk_test_51QD0OqRwgyy5ljInlrYOZ55FKPnQBJmqOHLtkT3Ew0O67BpYiwMmBY9shoYbgYEMkIIeeiFUieBx7VybFchbfEGn00wjbXU07T"
  );

  const handleSubscribe = (planId) => {
    setLoading(true);

    axios
      .post(
        "http://localhost:8000/api/subscription-app/subscribe",
        {
          subscription_plan: planId,
          user: "1", // static user id
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNTI3ODAyLCJpYXQiOjE3Mjk2NjM4MDIsImp0aSI6IjQxYWNmM2Q0ZDE5MzQzYzA4ZjQ4YTQ3NDdmMGY1MTZlIiwidXNlcl9pZCI6MX0.vsNeR82VsmXyAoAscawc9jnC64n2Xdd6KqPduVNk2es`,
          },
        }
      )
      .then((response) => {
        const sessionId = response.data.session_id;

        // Redirect to Stripe Checkout page
        stripePromise.then((stripe) => {
          stripe.redirectToCheckout({ sessionId });
        });
      })
      .catch((error) => {
        setLoading(false);
        console.error("Error creating subscription", error);
      });
  };

  return (
    <Elements stripe={stripePromise}>
      <section>
        <h1>Select your Plan</h1>
        <div className="plan-container">
          {data.map((plan) => (
            <div className="plan-card" key={plan.id}>
              <h2>{plan.name}</h2>
              <p>{plan.description}</p>
              <p>
                <strong>${plan.price}/month</strong>
              </p>
              <button
                onClick={() => handleSubscribe(plan?.id)}
                disabled={loading}
              >
                {loading ? "Processing..." : "Subscribe"}
              </button>
            </div>
          ))}
        </div>
      </section>
    </Elements>
  );
}

export default App;
