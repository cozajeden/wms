import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Menu() {
  const { username } = useAuth();
  return (
    <>
      <div>
        <h1>Menu</h1>
        <Link to="/app/dashboard">Dashboard</Link><br/>
        <Link to="/users/logout">Logout ({username})</Link>
      </div>
    </>
  )
}

export default Menu
