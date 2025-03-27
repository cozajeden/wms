import { Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';

function Interface() {
  return (
    <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  )
}

export default Interface
