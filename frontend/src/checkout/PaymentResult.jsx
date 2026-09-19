import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, formatMoney, newAttempt } from './api';
import { gateways } from './gateways';

export default function PaymentResult() {
  const { paymentId } = useParams();
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);
  const [retry, setRetry] = useState(0);
  const params = new URLSearchParams(window.location.search);
  const cancelled = params.get('cancelled') === '1';
  const transactionId = params.get('transaction_id');

  useEffect(() => {
    let active = true;
    setBusy(true);
    setError('');
    const body = transactionId ? { transaction_id: transactionId } : {};
    api(`/payments/${paymentId}`).then((saved) => {
      if (active) setPayment(saved);
      return api(`/payments/${paymentId}/verify`, { method: 'POST', body });
    }).then((verified) => { if (active) setPayment(verified); })
      .catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [paymentId, retry, transactionId]);

  const paid = payment?.status === 'paid';
  const title = paid ? 'Payment confirmed' : payment?.status === 'failed' ? 'Payment unsuccessful' : cancelled ? 'You left checkout' : 'Checking your payment';
  return <section className="panel result" aria-busy={busy}>
    <span className={`result-icon ${paid ? 'paid' : ''}`} aria-hidden="true">{paid ? '✓' : '↻'}</span>
    <span className="eyebrow">{payment?.mode === 'mock' ? 'SIMULATED RESULT' : 'PAYMENT RESULT'}</span>
    <h1>{title}</h1>
    <p aria-live="polite">{busy ? 'Retrieving the latest status from the backend…' : paid ? (payment.mode === 'mock' ? 'The local simulation completed. No money moved.' : 'The provider confirmed the saved reference, amount and currency.') : 'No payment has been confirmed. You can check again, or start a new checkout.'}</p>
    {payment && <dl className="receipt"><div><dt>Gateway</dt><dd>{gateways[payment.gateway].name}</dd></div><div><dt>Amount</dt><dd>{formatMoney(payment.amount_minor, payment.currency)}</dd></div><div><dt>Status</dt><dd><span className={`status ${payment.status}`}>{payment.status}</span></dd></div><div><dt>Mode</dt><dd>{payment.mode}</dd></div><div><dt>Reference</dt><dd className="reference">{payment.id}</dd></div></dl>}
    {error && <p className="error" role="alert">{error}</p>}
    <div className="actions">{!paid && <button disabled={busy} onClick={() => setRetry(retry + 1)}>Check status again</button>}{payment?.status === 'pending' && <a className="button" href={payment.checkout_url}>Resume checkout</a>}<Link className="button primary" to="/" onClick={newAttempt}>New checkout</Link></div>
    <p className="hint">Redirect parameters never decide the result. Webhooks can confirm a payment even if you close the checkout page.</p>
  </section>;
}
