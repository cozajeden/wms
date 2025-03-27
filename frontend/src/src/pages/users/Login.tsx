import { useAuth } from '../../contexts/AuthContext'
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const handleLogin = async (e: React.FormEvent<HTMLFormElement> | React.MouseEvent<HTMLButtonElement>) => {
    
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/', { replace: true });
    } catch (error) {
      console.error('Login failed:', error);
    }
  }

  return (
    <>
      <div>
        <h1>Login</h1>
        <form>
          <input type="text" name="username" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input type="password" name="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
          <button type="submit" onClick={handleLogin}>Login</button>
        </form>
      </div>
    </>
  )
}

export default Login
