import React, { useState } from "react";
import "./StandardCheckout.css";
import {
  PayPalScriptProvider,
  PayPalButtons,
  ReactPayPalScriptOptions,
  PayPalButtonsComponentProps,
} from "@paypal/react-paypal-js";

// Renders errors or successfull transactions on the screen.
function Message({ content }) {
  return <p>{content}</p>;
}

function PaypalStandardCheckout() {
  const BASE_URL = import.meta.env.VITE_BASE_URL;

  /**
   * @see Complete JS SDK Info: https://developer.paypal.com/sdk/js/reference/
   */
  const initialOptions: ReactPayPalScriptOptions = {
    clientId: "test",
    "enable-funding": "venmo",
    "disable-funding": "",
    "buyer-country": "US",
    currency: "USD",
    "data-page-type": "product-details",
    components: "buttons",
    "data-sdk-integration-source": "developer-studio",
  };

  const [message, setMessage] = useState("");

  const createOrder: PayPalButtonsComponentProps["createOrder"] = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // use the "body" param to optionally pass additional order information
        // like product ids and quantities
        body: JSON.stringify({
          cart: [
            {
              id: "1", // product id
              quantity: "5",
            },
          ],
        }),
      });

      const orderData = await response.json();

      if (orderData.id) {
        return orderData.id;
      } else {
        const errorDetail = orderData?.details?.[0];
        const errorMessage = errorDetail
          ? `${errorDetail.issue} ${errorDetail.description} (${orderData.debug_id})`
          : JSON.stringify(orderData);

        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error(error);
      setMessage(`Could not initiate PayPal Checkout...${error}`);
    }
  };

  const onApprove: PayPalButtonsComponentProps["onApprove"] = async (
    data,
    actions
  ) => {
    console.log(data, "data..........->>>>>>>>>>");
    try {
      const response = await fetch(
        `${BASE_URL}/api/orders/${data.orderID}/capture`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const orderData = await response.json();
      // Three cases to handle:
      //   (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
      //   (2) Other non-recoverable errors -> Show a failure message
      //   (3) Successful transaction -> Show confirmation or thank you message

      const errorDetail = orderData?.details?.[0];

      if (errorDetail?.issue === "INSTRUMENT_DECLINED") {
        // (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
        // recoverable state, per https://developer.paypal.com/docs/checkout/standard/customize/handle-funding-failures/
        return actions.restart();
      } else if (errorDetail) {
        // (2) Other non-recoverable errors -> Show a failure message
        throw new Error(`${errorDetail.description} (${orderData.debug_id})`);
      } else {
        // (3) Successful transaction -> Show confirmation or thank you message
        // Or go to another URL:  actions.redirect('thank_you.html');
        const transaction = orderData.purchase_units[0].payments.captures[0];
        setMessage(
          `Transaction ${transaction.status}: ${transaction.id}. See console for all available details`
        );
        console.log(
          "Capture result",
          orderData,
          JSON.stringify(orderData, null, 2)
        );
      }
    } catch (error) {
      console.error(error);
      setMessage(`Sorry, your transaction could not be processed...${error}`);
    }
  };

  const onCancel: PayPalButtonsComponentProps["onCancel"] = (data) => {
    // Show a cancel page, or return to cart
    window.location.assign("/your-cancel-page");
  };

  const onError: PayPalButtonsComponentProps["onError"] = (err) => {
    // For example, redirect to a specific error page
    window.location.assign("/your-error-page-here");
  };

  return (
    <div className="container">
      <PayPalScriptProvider options={initialOptions}>
        <PayPalButtons
          /**
           * @see Options: https://developer.paypal.com/sdk/js/reference/#link-paypalbuttonsoptions
           */
          style={{
            shape: "rect",
            layout: "vertical",
            color: "gold",
            label: "paypal",
          }}
          createOrder={createOrder}
          onApprove={onApprove}
          // onError={onError}
          // onCancel={onCancel}
        />
      </PayPalScriptProvider>
      <Message content={message} />
    </div>
  );
}

export default PaypalStandardCheckout;
