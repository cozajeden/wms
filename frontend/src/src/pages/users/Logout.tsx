import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom';

function Logout() {
  const { logout, username } = useAuth();
  const navigate = useNavigate();
  const handleLogout = async (e: React.FormEvent<HTMLFormElement> | React.MouseEvent<HTMLButtonElement>) => {
    
    e.preventDefault();
    try {
      await logout();
      navigate('/users/login', { replace: true });
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  return (
    <>
      <div>
        <h1>Logout</h1>
        <form>
          <h1>Are you sure you ({username}) want to logout?</h1>
          <button type="submit" onClick={handleLogout}>Logout</button>
          <button type="button" onClick={() => navigate('/', { replace: true })}>Back</button>
        </form>
      </div>
    </>
  )
}

export default Logout
