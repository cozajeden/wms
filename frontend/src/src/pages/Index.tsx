import Menu from '../components/Menu'
import { Outlet } from 'react-router-dom'

function Index() {
  return (
    <>
        <Menu />
        <Outlet />
    </>
  )
}

export default Index
