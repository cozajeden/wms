import { useAuth } from '../../contexts/AuthContext'
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

function RegisterCompany() {
  const { registerCompany } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [domain, setDomain] = useState('');
  const [error, setError] = useState('');

  const handleRegisterCompany = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    try {
      await registerCompany(username, password, email, name, domain);
      navigate('/users/login', { replace: true });
    } catch (e: any) {
      console.error('Register failed:', e);
      for (const key in e.response.data) {
        setError(e.response.data[key]);
      }
    }
  }

  return (
    <>
      <div>
        <h1>Register Company</h1>
        {error && <p>{error}</p>}
        <form>
          <label htmlFor="name">Company Name: </label>
          <input type="text" name="name" placeholder="Company Name" value={name} onChange={(e) => setName(e.target.value)} /><br />
          <label htmlFor="domain">Domain: </label>
          <input type="text" name="domain" placeholder="Domain" value={domain} onChange={(e) => setDomain(e.target.value)} /><br />
          <label htmlFor="email">Email: </label>
          <input type="email" name="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} /><br />
          <label htmlFor="username">Username: </label>
          <input type="text" name="username" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} /><br />
          <label htmlFor="password">Password: </label>
          <input type="password" name="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/><br />
          <button type="submit" onClick={handleRegisterCompany}>Register</button>
        </form>
        <p>Already have an account? <Link to="/users/login">Login</Link></p>
      </div>
    </>
  )
}

export default RegisterCompany
