import { useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const PayStackPaymentCallback = () => {
  const [searchParams] = useSearchParams();
  const reference = searchParams.get("reference");
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!reference) {
      toast.error("Invalid payment reference.");
      navigate("/paystack");
      return;
    }

    if (!hasFetched.current) {
      hasFetched.current = true; // Set flag to true
      verifyTransaction(reference);
    }
  }, [reference, navigate]);

  const verifyTransaction = async (reference) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/checkout/paystack/verify-payment/${reference}`
      );
      if (response?.status === 200) {
        toast.success("Payment successful!");
        navigate("/paystack");
      } else {
        toast.error("Payment verification failed.");
        navigate("/paystack");
      }
    } catch (error) {
      toast.error(error);
      window.location.reload(); // try-again
    }
  };

  return (
    <div className="text-center p-10">
      <h2 className="text-xl font-bold">Verifying Payment...</h2>
      <p>Please wait while we confirm your transaction.</p>
    </div>
  );
};

export default PayStackPaymentCallback;
