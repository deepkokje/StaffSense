import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "antd/dist/reset.css";

import App from "./App";
import AppProviders from "./AppProviders";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("The application root element is missing.");
}

createRoot(rootElement).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
