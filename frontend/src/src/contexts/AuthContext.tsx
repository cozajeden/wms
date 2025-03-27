import { createContext, useState, useEffect, useContext } from "react";
import axios from "axios";

interface AuthContextType {
    username: string | null;
    isAuthenticated: boolean;
    accessToken: string | null;
    refreshToken: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    init: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [accessToken, setAccessToken] = useState<string | null>(null);
    const [refreshToken, setRefreshToken] = useState<string | null>(null);
    
    useEffect(() => {
        if (accessToken) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        }
    }, [accessToken]);

    const init = () => {
        try {
            const username = localStorage.getItem('username');
            if (username) {
                setUsername(username);
            }
            const accessToken = localStorage.getItem('accessToken');
            if (accessToken) {
                setAccessToken(accessToken);
            }
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken)   {
                setRefreshToken(refreshToken);
            }
            if (username && accessToken && refreshToken) {
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.error('Error initializing auth:', error);
            throw error;
        }
    };

    const login = async (username: string, password: string) => {
        try {
            const response = await api.post('/users/login/', {
                username,
                password,
            });
            setUsername(username);
            setAccessToken(response.data.access);
            setRefreshToken(response.data.refresh);
            localStorage.setItem('username', username);
            localStorage.setItem('accessToken', response.data.access);
            localStorage.setItem('refreshToken', response.data.refresh);
            setIsAuthenticated(true);
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const logout = () => {
        setAccessToken(null);
        setRefreshToken(null);
        setIsAuthenticated(false);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    };

    return (
        <AuthContext.Provider value={{ username, isAuthenticated, accessToken, refreshToken, login, logout, init }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const auth = useContext(AuthContext);
    if (!auth) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return auth;
};
