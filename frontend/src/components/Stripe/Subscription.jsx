import axios from "axios";
import "./Subscription.css";
import { useEffect, useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";

function StripeSubscription() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSubscriptionPlans = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/v1/public/subscription-app/subscription-plans"
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
        "http://localhost:8000/api/v1/public/subscription-app/subscribe-plan",
        {
          subscription_plan: "a6a0159c-b2b4-4f94-8136-5610304621f7",
          user: "f0b51ec9-260a-4d45-bb41-1abd53e6bd4e", // static user id
          paymentMethod: "STRIPE"
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNjI5MjE4LCJpYXQiOjE3MzAwMjQ0MTgsImp0aSI6ImQxMDQ4MWNkNzI0ZDQ3ZTM4ZjFiMzZiYjNmZmQxZDNlIiwidXNlcl9pZCI6M30.7Fe2ufJPO8k6aIf-GnotOZhR5wyg1yUmET-w0PostRE`,
          },
        }
      )
      .then((response) => {
        const sessionId = response.data.sessionId;

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

export default StripeSubscription;
