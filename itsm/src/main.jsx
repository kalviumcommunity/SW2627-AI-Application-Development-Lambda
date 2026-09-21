import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { ChatProvider } from './context/ChatContext'
import { IncidentsProvider } from './context/IncidentsContext'
import Layout from './components/layout/Layout'
import IncidentsPage from './pages/IncidentsPage.jsx'
import IncidentDetailPage from './pages/IncidentDetailPage.jsx'
import CreateIncidentPage from './pages/CreateIncidentPage.jsx'
import KnowledgePage from './pages/KnowledgePage.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <IncidentsProvider>
      <ChatProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<IncidentsPage />} />
              <Route path="/incident/new" element={<CreateIncidentPage />} />
              <Route path="/incident/:id" element={<IncidentDetailPage />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ChatProvider>
    </IncidentsProvider>
  </StrictMode>,
)
