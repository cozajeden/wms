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
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleRegisterCompany = async () => {
    try {
      await registerCompany(username, password, email, name, domain);
      navigate('/users/login', { replace: true });
    } catch (e: any) {
      console.error('Register failed:', e);
      setErrors(e.response.data);
    }
  }

  const getFieldError = (fieldName: string) => {
    return errors[fieldName] ? <div style={{ color: 'red'}}>{errors[fieldName]}</div> : null;
  }

  const getGeneralError = () => {
    const generalErrors = Object.entries(errors)
      .filter(([key]) => !['name', 'email', 'domain'].includes(key))
      .map(([_, value]) => value);
    
    return generalErrors.length > 0 ? (
      <div style={{ color: 'red'}}>{generalErrors.join(', ')}</div>
    ) : null;
  }

  return (
    <>
      <div>
        <h1>Register Company</h1>
        <p>Please fill in the following fields to register a new company.</p>
        <p>Username and password are used to login to the platform.</p>
        {getGeneralError()}
        <form className="register-form" onSubmit={(e) => {
          e.preventDefault();
          handleRegisterCompany();
        }}>
          <label htmlFor="username">Username: </label>
          <input type="text" name="username" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
          {getFieldError('username')}
          <br />
          <label htmlFor="password">Password: </label>
          <input type="password" name="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {getFieldError('password')}
          <br />
          <label htmlFor="name">Company Name: </label>
          <input type="text" name="name" placeholder="Company Name" value={name} onChange={(e) => setName(e.target.value)} required />
          {getFieldError('name')}
          <br />
          <label htmlFor="domain">Domain: </label>
          <input type="text" name="domain" placeholder="Domain" value={domain} onChange={(e) => setDomain(e.target.value)} required />
          {getFieldError('domain')}
          <br />
          <label htmlFor="email">Email: </label>
          <input type="email" name="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          {getFieldError('email')}
          <br />
          <button type="submit">Register</button>
        </form>
        <p>Already have an account? <Link to="/users/login">Login</Link></p>
      </div>
    </>
  )
}

export default RegisterCompany
