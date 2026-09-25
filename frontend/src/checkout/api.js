const ROOT = "/api/checkout";

function errorMessage(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(errorMessage).join(" ");
  if (value && typeof value === "object")
    return Object.entries(value)
      .map(([key, message]) => `${key}: ${errorMessage(message)}`)
      .join(" ");
  return "Request failed. Please try again.";
}

export async function api(
  path,
  { method = "GET", body, headers, signal } = {},
) {
  const response = await fetch(`${ROOT}${path}`, {
    method,
    signal,
    headers: { "Content-Type": "application/json", ...headers },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new Error(
      data
        ? errorMessage(data)
        : "The backend is unavailable. Start Django on port 8000.",
    );
  if (!data)
    throw new Error(
      "Unexpected response. Check that Django is running on port 8000.",
    );
  return data;
}

export function formatMoney(amount, currency) {
  return new Intl.NumberFormat("en", { style: "currency", currency }).format(
    amount / 100,
  );
}

// Preserve a pending request across reloads; a network retry must use the same key.
let memoryAttempt = null;

export function checkoutKey(body) {
  const fingerprint = JSON.stringify(body);
  let saved = memoryAttempt;
  try {
    saved =
      JSON.parse(sessionStorage.getItem("checkout-attempt") || "null") || saved;
  } catch {
    // Corrupt or disabled session storage must not prevent checkout.
  }
  if (saved?.fingerprint === fingerprint && typeof saved.key === "string")
    return saved.key;
  const key = crypto.randomUUID();
  memoryAttempt = { fingerprint, key };
  try {
    sessionStorage.setItem("checkout-attempt", JSON.stringify(memoryAttempt));
  } catch {
    /* Keep the in-memory key for retries. */
  }
  return key;
}

export function newAttempt() {
  memoryAttempt = null;
  try {
    sessionStorage.removeItem("checkout-attempt");
  } catch {
    /* Storage may be disabled. */
  }
}
