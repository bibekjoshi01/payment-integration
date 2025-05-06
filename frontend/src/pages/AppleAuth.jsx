import AppleSignin from "react-apple-signin-auth";

import React, { useState } from "react";
import AppleLogin from "react-apple-login";

export const AppleButton = () => {
  const [authResponse, setAuthResponse] = useState({});

  const appleResponse = (response) => {
    if (!response.error) {
      setAuthResponse(response);
    } else {
      console.error("Apple login failed:", response.error);
    }
  };

  return (
    <div>
      {Object.keys(authResponse).length === 0 ? (
        <AppleLogin
          clientId="com.noticepark.test.sid"
          redirectURI="https://www.gravitylifestyle.com.np/login"
          usePopup={true}
          callback={appleResponse}
          scope="email name"
          responseMode="query"
          render={(renderProps) => (
            <button
              onClick={renderProps.onClick}
              style={{
                backgroundColor: "black",
                padding: 10,
                border: "1px solid black",
                fontFamily: "none",
                lineHeight: "25px",
                fontSize: "25px",
              }}
            >
              <i className="fa-brands fa-apple px-2 "></i>
              Continue with Apple
            </button>
          )}
        />
      ) : (
        <p style={{ fontFamily: "none" }}>
          {JSON.stringify(authResponse, null, 2)}
        </p>
      )}
    </div>
  );
};

const MyAppleSigninButton = () => {
  const handleSuccess = (response) => {
    console.log("Apple Sign-In Success:", response);
  };

  const handleError = (error) => {
    console.error("Apple Sign-In Error:", error);
  };

  return (
    <AppleSignin
      authOptions={{
        clientId: "com.noticepark.test.sid",
        scope: "email name",
        redirectURI: "https://www.gravitylifestyle.com.np/login",
        state: Math.random().toString(36).substring(2),
        nonce: Math.random().toString(36).substring(2),
        usePopup: true,
      }}
      onSuccess={handleSuccess}
      onError={handleError}
      uiType="dark"
      className="apple-auth-btn"
      buttonExtraChildren="Continue with Apple"
    />
  );
};

export default MyAppleSigninButton;
