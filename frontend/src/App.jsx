import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import Checkout from './checkout/Checkout';
import PaymentResult from './checkout/PaymentResult';
import Simulator from './checkout/Simulator';
import './App.css';

export default function App() {
  return <BrowserRouter>
    <header className="site-header"><Link className="brand" to="/"><span aria-hidden="true">↗</span> Payment playground</Link><span className="header-note">React + Django</span></header>
    <main><Routes>
      <Route path="/" element={<Checkout />} />
      <Route path="/return/:paymentId" element={<PaymentResult />} />
      <Route path="/simulate/:paymentId" element={<Simulator />} />
      <Route path="*" element={<section className="panel"><h1>Page not found</h1><Link to="/">Open checkout</Link></section>} />
    </Routes></main>
    <footer>PayPal · Stripe · Paystack · Flutterwave</footer>
  </BrowserRouter>;
}
