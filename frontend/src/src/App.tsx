import { Routes, Route } from 'react-router-dom';
import { useEffect } from 'react'
import { useAuth } from './contexts/AuthContext'
import Index from './pages/Index';
import Users from './pages/users/Index';
import Dashboard from './pages/app/Dashboard';
import Auth from './pages/users/AuthApp';
import './App.css';

function App() {
  const { init, isAuthenticated } = useAuth();

    useEffect(() => {
      init();
  }, []);

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/*" element={<Auth />} />
      </Routes>
    )
  }

  return (
    <Routes>
        <Route path="/" element={<Index />}>
        <Route path="users/*" element={<Users />} />
        <Route path="app/*" element={<Dashboard />} />
        </Route>
    </Routes>
  )
}

export default App
