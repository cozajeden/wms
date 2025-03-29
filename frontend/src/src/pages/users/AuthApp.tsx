import { Routes, Route } from 'react-router-dom';
import RegisterCompany from './RegisterCompany'
import Login from './Login'

function Auth() {
return (
    <Routes>
        <Route path="/" element={<RegisterCompany />} />
        <Route path="/users/login" element={<Login />} />
    </Routes>
)
}

export default Auth
