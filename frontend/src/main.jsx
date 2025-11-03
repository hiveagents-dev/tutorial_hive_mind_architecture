import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import '../styles_base.css'
import '../styles_layout.css'
import '../styles_components.css'
import '../styles.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

