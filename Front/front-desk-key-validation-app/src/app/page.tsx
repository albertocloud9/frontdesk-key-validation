"use client";
import React, { useEffect, useRef, useState } from "react";
import jsQR from "jsqr";
import axios from "axios";
import { Spinner } from "./components/Spinner";

const QRCodeScanner = () => {
  const videoRef = useRef(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scannedResult, setScannedResult] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!scannedResult) {
      const video = videoRef.current;

      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");

      let stream;

      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((mediaStream) => {
          stream = mediaStream;
          video.srcObject = stream;
        })
        .catch((err) => {
          console.error("Error accessing the camera: ", err);
        });

      video.addEventListener("play", () => {
        const scan = () => {
          if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = context.getImageData(
              0,
              0,
              canvas.width,
              canvas.height
            );
            const qrCode = jsQR(
              imageData.data,
              imageData.width,
              imageData.height
            );

            if (qrCode && qrCode.data) {
              try {
                const sanitizedData = qrCode.data.replace(/'/g, '"');
                const scannedData = JSON.parse(sanitizedData);

                setScannedResult(scannedData);
                setIsScanning(true);
                setMessage("Successfull");

              } catch (error) {
                console.error("Error parsing QR code data:", error);
                setMessage("This QR is not a key QR, Please try again");
              }
            }
          }
          requestAnimationFrame(scan);
        };

        scan();
      });

      return () => {
        // Stop the video stream when the component unmounts
        if (stream) {
          stream.getTracks().forEach((track) => track.stop());
        }
      };
    }
  }, []);

  // useEffect(() => {
  //   if (scannedResult) {
  //     const video = videoRef.current;

  //     let stream;

  //     navigator.mediaDevices
  //       .getUserMedia({ video: true })
  //       .then((mediaStream) => {
  //         stream = mediaStream;
  //         video.srcObject = stream;
  //       })
  //       .catch((err) => {
  //         console.error("Error accessing the camera: ", err);
  //       });

  //     if (stream) {
  //       stream.getTracks().forEach((track) => track.stop());
  //     }
  //   }
  // }, [scannedResult]);

// useEffect(() => {
//   if (scannedResult) {
//     const sendPostRequest = async () => {
//       try {
//         // Define the URL and headers
//         const url =
//           "https://us-central1-main-cloud9.cloudfunctions.net/front_desk_key_validator";
//         const headers = {
//           // Authorization: `bearer ${}`, // Make sure to replace or fetch gcloudAuthToken dynamically
//           "Content-Type": "application/json",
//         };
//         // Make the POST request with axios
//         const response = await axios.post(url, scannedResult, { headers });

//         console.log("Response:", response.data);
//         setMessage(`Request successful! ${response.data}`);
//       } catch (error) {
//         console.error("Error making the request to servicee :", error);
//         setMessage("Failed to send data.");
//       }
//     };

//     sendPostRequest();
//   }
// }, [scannedResult]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#A54E27] text-white p-4">
      <h1 className="text-3xl font-bold mb-8">QR Code Scanner</h1>

      {isScanning ? (
        <div className="absolute inset-0 flex items-center justify-center bg-[#A54E27]/80">
          <Spinner />
        </div>
      ) : (
        <video
          id="video"
          width="640"
          height="480"
          autoPlay
          ref={videoRef}
        ></video>
      )}
      {scannedResult && (
        <div className="mt-4">
          <h2 className="text-2xl font-bold">Scanned Data:</h2>
          <pre className="bg-white text-[#A54E27] p-4 rounded-lg overflow-auto">
            {JSON.stringify(scannedResult, null, 2)}
          </pre>
        </div>
      )}
      {message && (
        <p id="result_message" className="text-2xl mt-4">
          {message}
        </p>
      )}
    </div>
  );
};

export default QRCodeScanner;
