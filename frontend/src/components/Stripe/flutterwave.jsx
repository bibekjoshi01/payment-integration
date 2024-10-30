import { useFlutterwave, closePaymentModal } from "flutterwave-react-v3";

export default function Flutterwave() {
  const config = {
    public_key: "FLWPUBK_TEST-e06002d6740b7993930958839786adf3-X",
    tx_ref: Date.now(),
    amount: 100,
    currency: "NGN",
    payment_options: "card",
    payment_plan: "69934",
    customer: {
      email: "user@gmail.com",
      phone_number: "070********",
      name: "john doe",
    },
    meta: { counsumer_id: "7898", consumer_mac: "kjs9s8ss7dd" },
    customizations: {
      title: "my Payment Title",
      description: "Payment for items in cart",
      logo: "https://st2.depositphotos.com/4403291/7418/v/450/depositphotos_74189661-stock-illustration-online-shop-log.jpg",
    },
  };

  const handleFlutterPayment = useFlutterwave(config);

  return (
    <div className="Flutterwave">
      <h1>Hello Test user</h1>

      <button
        onClick={() => {
          handleFlutterPayment({
            callback: (response) => {
              console.log(response, "response >>");
              closePaymentModal(); // this will close the modal programmatically
            },
            onClose: () => {},
          });
        }}
      >
        Payment with React hooks
      </button>
    </div>
  );
}
