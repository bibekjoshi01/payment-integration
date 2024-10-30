import React from "react";
import "./Donate.css"; // Add CSS styling in a separate file

const Donate = () => {
  const redirectToLink = (link) => {
    window.open(link, "_blank");
  };

  return (
    <div className="donate-container">
      <h1 className="donate-header">Support Our Cause</h1>
      <p className="donate-description">
        Every contribution helps us get closer to our goals. Choose a platform
        below to donate securely.
      </p>
      <div className="button-group">
        <button
          className="btn paypal"
          onClick={() =>
            redirectToLink(
              "https://www.sandbox.paypal.com/donate/?hosted_button_id=J7BDYLYGLVGZW"
            )
          }
        >
          Donate with PayPal
        </button>
        <button
          className="btn stripe"
          onClick={() =>
            redirectToLink("https://donate.stripe.com/test_28odTZ0ZI54ygfe9AA")
          }
        >
          Donate with Stripe
        </button>
        <button
          className="btn fw"
          onClick={() =>
            redirectToLink("https://sandbox.flutterwave.com/donate/thg2tlz5z2l6")
          }
        >
          Donate with Flutterwave
        </button>
      </div>
    </div>
  );
};

export default Donate;
