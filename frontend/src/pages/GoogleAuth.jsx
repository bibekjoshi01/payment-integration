// import { useState } from "react";
// import { GoogleLogin } from "@react-oauth/google";

// const GoogleAuth = () => {
//   const handleSuccess = (response) => {
//     console.log(response);
//   };

//   const handleError = () => {
//     console.log("Login Failed");
//   };

//   return (
//     <div style={{ textAlign: "center", marginTop: "50px" }}>
//       <h2>Google OAuth Login</h2>
//       <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
//     </div>
//   );
// };

// export default GoogleAuth;

import { useGoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

const GoogleAuth = () => {
  const navigate = useNavigate();

  const responseGoogle = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        console.log(tokenResponse);
        navigate("/paystack");
      } catch (error) {
        console.log(error);
      }
    },
  });

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Google OAuth Login</h2>
      <button onClick={responseGoogle}> Login with Google </button>
    </div>
  );
};

export default GoogleAuth;
