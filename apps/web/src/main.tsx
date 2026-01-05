
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import App from "./App"
import AdminApp from "./AdminApp"
import Engagement from "./Engagement"
import LearningStyle from "./LearningStyle"
import AdminSignin from "./AdminSignin"
import UserSignin from "./UserSignin"
import Navbar from "./Navbar"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<AdminApp />} />
        <Route path="/admin-signin" element={<AdminSignin />} />
        <Route path="/user-signin" element={<UserSignin />} />
        <Route path="/engagement" element={<Engagement />} />
        <Route path="/learning-style" element={<LearningStyle />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
