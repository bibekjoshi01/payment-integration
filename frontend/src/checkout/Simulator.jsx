import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, formatMoney } from './api';
import { gateways } from './gateways';

export default function Simulator() {
  const { paymentId } = useParams();
  const navigate = useNavigate();
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    api(`/payments/${paymentId}`, { signal: controller.signal }).then(setPayment).catch((err) => {
      if (err.name !== 'AbortError') setError(err.message);
    });
    return () => controller.abort();
  }, [paymentId]);

  async function simulate(outcome) {
    setBusy(true);
    setError('');
    try {
      await api(`/payments/${paymentId}/simulate`, { method: 'POST', body: { outcome } });
      navigate(`/return/${paymentId}`);
    } catch (err) { setError(err.message); setBusy(false); }
  }

  return <section className="panel result">
    <span className="eyebrow">LOCAL SIMULATOR</span><h1>Choose a test outcome.</h1>
    <p>This screen simulates hosted checkout. It does not contact a payment provider or collect card details.</p>
    {payment && <p className="simulation-total">{gateways[payment.gateway].name} · {formatMoney(payment.amount_minor, payment.currency)}</p>}
    {payment?.mode === 'mock' && <div className="actions"><button className="primary" disabled={busy} onClick={() => simulate('paid')}>Simulate success</button><button disabled={busy} onClick={() => simulate('failed')}>Simulate failure</button><Link className="button" to={`/return/${paymentId}?cancelled=1`}>Cancel checkout</Link></div>}
    {payment && payment.mode !== 'mock' && <p className="error">This is a provider sandbox payment. Simulation is unavailable.</p>}
    {error && <p className="error" role="alert">{error}</p>}
    {!payment && !error && <p aria-live="polite">Loading checkout…</p>}
    <Link to="/">Back to checkout</Link>
  </section>;
}
