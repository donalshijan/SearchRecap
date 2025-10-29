import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { FlashcardProvider } from "./contexts/FlashcardContext";
import './index.css'
import App from './App.jsx'
import { ConfigProvider } from "./contexts/ConfigContext";

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ConfigProvider>
      <FlashcardProvider>
        <App />
      </FlashcardProvider>
    </ConfigProvider>
  </StrictMode>,
)
