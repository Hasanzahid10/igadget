import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import API from './api/axios';

// Component & Page Imports
import AuthModal from './components/AuthModal';
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';

// Icons
import { User, LogOut, ShieldCheck, Home as HomeIcon, ShoppingBag } from 'lucide-react';

// Protected Route Wrapper for Authenticated Users
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/" replace />;
  }
  return children;
};

// Protected Route Wrapper for Admin Users Only
const AdminRoute = ({ user, children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/" replace />;
  }
  // Checks if user has admin role or staff status
  if (user && (user.role === 'admin' || user.is_staff)) {
    return children;
  }
  return <div style={{ padding: '40px', textAlign: 'center' }}>Access Denied. Admin privileges required.</div>;
};

// Home Component Placeholder
function HomePage({ onOpenAuth, currentUser }) {
  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px', textAlign: 'center' }}>
      <h1 style={{ fontSize: '32px', color: '#0f172a' }}>Welcome to iGadget Store</h1>
      <p style={{ color: '#64748b' }}>Explore our catalog of latest gadgets and accessories.</p>
      
      {!currentUser && (
        <button 
          onClick={onOpenAuth}
          style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', marginTop: '20px' }}
        >
          Sign In / Create Account
        </button>
      )}
    </div>
  );
}

export default function App() {
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch current user details on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const res = await API.get('users/me/');
      setCurrentUser(res.data);
    } catch (err) {
      console.error("Session expired or invalid token:", err);
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setCurrentUser(null);
    window.location.href = '/';
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Inter, sans-serif' }}>Loading iGadget Application...</div>;
  }

  return (
    <Router>
      <div style={{ fontFamily: 'Inter, sans-serif', minHeight: '100vh', backgroundColor: '#f8fafc' }}>
        
        {/* GLOBAL NAVIGATION HEADER BAR */}
        <nav style={{ backgroundColor: '#0f172a', color: '#fff', padding: '14px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '25px' }}>
            <Link to="/" style={{ color: '#10b981', textDecoration: 'none', fontWeight: 'bold', fontSize: '22px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShoppingBag size={22} /> iGadget
            </Link>
            <Link to="/" style={{ color: '#cbd5e1', textDecoration: 'none', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <HomeIcon size={16} /> Home
            </Link>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            {currentUser ? (
              <>
                {/* User Profile Link */}
                <Link to="/profile" style={{ color: '#fff', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: '500' }}>
                  <User size={18} color="#10b981" /> {currentUser.name || currentUser.email}
                </Link>

                {/* Admin Dashboard Link (Only visible if role === 'admin' or is_staff) */}
                {(currentUser.role === 'admin' || currentUser.is_staff) && (
                  <Link to="/admin" style={{ color: '#f59e0b', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', fontWeight: 'bold', backgroundColor: 'rgba(245, 158, 11, 0.1)', padding: '6px 12px', borderRadius: '6px' }}>
                    <ShieldCheck size={18} /> Admin Dashboard
                  </Link>
                )}

                {/* Logout Button */}
                <button 
                  onClick={handleLogout} 
                  style={{ backgroundColor: 'transparent', border: '1px solid #475569', color: '#cbd5e1', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
                >
                  <LogOut size={14} /> Logout
                </button>
              </>
            ) : (
              <button 
                onClick={() => setIsAuthOpen(true)} 
                style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }}
              >
                Sign In
              </button>
            )}
          </div>
        </nav>

        {/* APPLICATION ROUTES */}
        <Routes>
          {/* Public Home Page */}
          <Route path="/" element={<HomePage onOpenAuth={() => setIsAuthOpen(true)} currentUser={currentUser} />} />
          
          {/* Protected Customer Profile Route */}
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />

          {/* Protected Admin Control Center Route */}
          <Route 
            path="/admin" 
            element={
              <AdminRoute user={currentUser}>
                <AdminDashboard />
              </AdminRoute>
            } 
          />

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* GLOBAL AUTHENTICATION MODAL */}
        <AuthModal 
          isOpen={isAuthOpen} 
          onClose={() => setIsAuthOpen(false)} 
          onLoginSuccess={() => {
            fetchCurrentUser();
          }} 
        />

      </div>
    </Router>
  );
}