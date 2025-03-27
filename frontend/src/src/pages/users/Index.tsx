import { Routes, Route } from 'react-router-dom';
import Login from './Login';
import Logout from './Logout';

function Users() {
  return (
    <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
    </Routes>
  )
}

export default Users
