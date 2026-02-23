import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  ChakraProvider,
  ColorModeScript,
} from "@chakra-ui/react";
import theme from "./theme"; // Nosso novo tema!
import App from "./components/App";
import { ToastProvider } from "./components/Toast/components/ToastContext";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ColorModeScript initialColorMode={theme.config.initialColorMode} />
    <ChakraProvider theme={theme}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </ChakraProvider>
  </StrictMode>,
);
