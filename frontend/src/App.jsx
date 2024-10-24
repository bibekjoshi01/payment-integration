import "./App.css";
import StripeCheckout from "./components/Stripe/Stripe";
import PaypalStandardCheckout from "./components/Paypal/StandardCheckout";
import Cart from "./components/Cart";

const App = () => {
  return (
    <div className="main">
      <div className="cart">
        <h2>My Cart</h2>
        <Cart />
      </div>
      <div className="payment">
        <h2>Checkout</h2>
        <PaypalStandardCheckout />
        <StripeCheckout />
      </div>
    </div>
  );
};

export default App;
