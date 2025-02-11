import { toast } from "react-toastify";

const Paystack = () => {
  const handlePayment = async () => {
    try {
      let response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/checkout/paystack/initiate-payment`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ amount: 5000 }),
        }
      );

      response = await response.json();

      if (response.status && response?.data.access_code) {
        window.location.href = response.data?.authorization_url;
      } else {
        toast.error("Failed to initialize transaction");
      }
    } catch (error) {
      toast.error("Payment error:", error);
    }
  };

  return (
    <div
      style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
    >
      <h1>PayStack Payment Gateway</h1>
      <button
        onClick={handlePayment}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Pay Via PayStack
      </button>
    </div>
  );
};

export default Paystack;
