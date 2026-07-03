import { Routes, Route } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout.jsx'
import ProtectedRoute from '../components/ProtectedRoute.jsx'

import Weeks from '../pages/Weeks.jsx'
import Contestants from '../pages/Contestants.jsx'
import Episodes from '../pages/Episodes.jsx'
import Dishes from '../pages/Dishes.jsx'
import Scores from '../pages/Scores.jsx'
import Statistics from '../pages/Statistics.jsx'
import Login from '../pages/Login.jsx'
import Dashboard from '../pages/Dashboard.jsx'
import AutomationLogs from '../pages/AutomationLogs.jsx'

export default function AppRouter() {
  return (
    <MainLayout>
      <Routes>
        {/* Public — mirrors the backend's public GET endpoints */}
        <Route path="/" element={<Weeks />} />
        <Route path="/contestants" element={<Contestants />} />
        <Route path="/episodes" element={<Episodes />} />
        <Route path="/dishes" element={<Dishes />} />
        <Route path="/scores" element={<Scores />} />
        <Route path="/statistics" element={<Statistics />} />
        <Route path="/login" element={<Login />} />

        {/* Admin-only */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/automation"
          element={
            <ProtectedRoute>
              <AutomationLogs />
            </ProtectedRoute>
          }
        />
      </Routes>
    </MainLayout>
  )
}
