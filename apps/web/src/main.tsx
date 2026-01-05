import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import "./index.css"

import AdminApp from "./AdminApp"
import AdminSignin from "./AdminSignin"
import App from "./App"
import Engagement from "./Engagement"
import LearningStyle from "./LearningStyle"
import Navbar from "./Navbar"
import UserSignin from "./UserSignin"
import XAIPrediction from "./components/XAIPrediction"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/analytics" element={<XAIPrediction />} />
        <Route path="/admin" element={<AdminApp />} />
        <Route path="/admin-signin" element={<AdminSignin />} />
        <Route path="/user-signin" element={<UserSignin />} />
        <Route path="/engagement" element={<Engagement />} />
        <Route path="/learning-style" element={<LearningStyle />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
