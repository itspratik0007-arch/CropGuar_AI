import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { PlantopediaPage } from './pages/PlantopediaPage';
import { NearbyStoresPage } from './pages/NearbyStoresPage';
import { DiseaseDetectionPage } from './pages/DiseaseDetectionPage';

export function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/disease"
            element={
              <ProtectedRoute>
                <DiseaseDetectionPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/plantopedia"
            element={
              <ProtectedRoute>
                <PlantopediaPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/stores"
            element={
              <ProtectedRoute>
                <NearbyStoresPage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
