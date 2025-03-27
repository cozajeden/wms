import Menu from '../components/Menu'
import { Outlet } from 'react-router-dom'
import Login from './users/Login'
import { useAuth } from '../contexts/AuthContext'

function Index() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <>
        <Menu />
        <Outlet />
    </>
  )
}

export default Index
