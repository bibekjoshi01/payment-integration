import { useEffect, useState } from "react";
import { api, checkoutKey, formatMoney } from "./api";
import { gateways } from "./gateways";

export default function Checkout() {
  const [config, setConfig] = useState(null);
  const [gateway, setGateway] = useState("paypal");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    api("/config", { signal: controller.signal })
      .then(setConfig)
      .catch((err) => {
        if (err.name !== "AbortError") setError(err.message);
      });
    return () => controller.abort();
  }, [reload]);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = { gateway, product: "demo-guide", email: email.trim() };
      const payment = await api("/payments", {
        method: "POST",
        body,
        headers: { "Idempotency-Key": checkoutKey(body) },
      });
      // Only redirect to URLs validated by the backend adapter.
      window.location.assign(payment.checkout_url);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!config)
    return (
      <section className="panel" aria-live="polite">
        <h1>Payment playground</h1>
        {error ? (
          <>
            <p role="alert">{error}</p>
            <button
              onClick={() => {
                setError("");
                setReload(reload + 1);
              }}
            >
              Retry connection
            </button>
          </>
        ) : (
          <p>Connecting to the checkout API…</p>
        )}
      </section>
    );

  const selected = config.gateways.find((item) => item.id === gateway);
  const product = config.products["demo-guide"];
  const amount = product.prices[selected.currency];
  const mock = config.mode === "mock";

  return (
    <>
      <div className="intro">
        <span className="eyebrow">FOUR GATEWAYS · ONE CHECKOUT</span>
        <h1>Try the payment flow.</h1>
        <p>Create an order, complete checkout, and see the verified result.</p>
      </div>
      <div className={`notice ${mock ? "" : "sandbox"}`}>
        <strong>{mock ? "Local simulator" : "Provider sandbox"}</strong>
        <span>
          {mock
            ? "No credentials or cards needed. Choose success or failure on the next screen."
            : "Uses provider test APIs. Use sandbox accounts and test cards only."}
        </span>
      </div>
      <div className="checkout-grid">
        <form className="panel" onSubmit={submit}>
          <h2>1. Choose a gateway</h2>
          <fieldset disabled={busy}>
            <legend className="sr-only">Payment gateway</legend>
            <div className="gateway-grid">
              {config.gateways.map((item) => {
                const info = gateways[item.id];
                return (
                  <label
                    className={`gateway ${gateway === item.id ? "selected" : ""}`}
                    key={item.id}
                  >
                    <input
                      type="radio"
                      name="gateway"
                      value={item.id}
                      checked={gateway === item.id}
                      onChange={() => {
                        setGateway(item.id);
                        setError("");
                      }}
                    />
                    <span
                      className="gateway-mark"
                      style={{ background: info.color }}
                      aria-hidden="true"
                    >
                      {info.mark}
                    </span>
                    <strong>{info.name}</strong>
                    <small>
                      {item.currency} ·{" "}
                      {item.ready
                        ? mock
                          ? "Simulator ready"
                          : "Test keys configured"
                        : "Keys needed"}
                    </small>
                  </label>
                );
              })}
            </div>
          </fieldset>
          <h2>2. Add a test email</h2>
          <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            maxLength={254}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            disabled={busy}
          />
          <p className="hint">
            Used for the provider checkout. Your email is not shown on the
            result page.
          </p>
          {!selected.ready && (
            <p className="error" role="status">
              Add {gateways[gateway].name} sandbox credentials to
              dj_server/.env, then restart Django.
            </p>
          )}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button
            className="primary"
            type="submit"
            disabled={busy || !selected.ready}
          >
            {busy
              ? "Creating checkout…"
              : mock
                ? "Open simulator →"
                : `Continue to ${gateways[gateway].name} →`}
          </button>
          <p className="hint">{gateways[gateway].detail}</p>
        </form>
        <aside className="panel order-summary">
          <span className="eyebrow">SAMPLE ORDER</span>
          <h2>{product.name}</h2>
          <p>{product.description}</p>
          <div className="price-line">
            <span>Total</span>
            <strong>{formatMoney(amount, selected.currency)}</strong>
          </div>
          <p className="hint">
            Prices are set by the server. USD and NGN amounts are separate demo
            prices, not exchange rates.
          </p>
          <hr />
          <h3>What happens next</h3>
          <ol className="steps">
            <li>The backend saves your order.</li>
            <li>You complete hosted checkout.</li>
            <li>The backend verifies payment details.</li>
          </ol>
          <a href={gateways[gateway].docs} target="_blank" rel="noreferrer">
            Read {gateways[gateway].name} documentation ↗
          </a>
        </aside>
      </div>
      <p className="footnote">
        A one-time payment example for learning and testing. Live payments are
        disabled.
      </p>
    </>
  );
}
