import { Routes, Route } from 'react-router-dom';
import { useEffect } from 'react'
import Index from './pages/Index';
import Users from './pages/users/Index';
import Dashboard from './pages/app/Dashboard';
import { useAuth } from './contexts/AuthContext'
import './App.css';

function App() {
  const { init } = useAuth();

    useEffect(() => {
      init();
  }, []);

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
