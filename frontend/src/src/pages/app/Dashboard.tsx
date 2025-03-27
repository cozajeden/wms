import { useAuth } from '../../contexts/AuthContext';

function Dashboard() {
  const { username } = useAuth();
  return (
    <>
      <div>
        <h1>Dashboard</h1>
        <p>Welcome {username}</p>
      </div>
    </>
  )
}

export default Dashboard
