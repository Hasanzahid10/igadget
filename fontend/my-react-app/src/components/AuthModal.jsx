import React, { useState } from 'react';
import { X, CheckCircle, Lock, Mail, User, ShieldCheck, KeyRound } from 'lucide-react';
import API from '../api/axios';

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  // Modes: 'login' | 'register' | 'otp' | 'forgot_password' | 'reset_password_otp'
  const [mode, setMode] = useState('login');
  
  // Form Inputs
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    new_password: '',
    first_name: '',
    last_name: '',
    otp: ''
  });

  const [registeredEmail, setRegisteredEmail] = useState('');
  const [devOtpCode, setDevOtpCode] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const clearMessages = () => {
    setErrorMsg('');
    setSuccessMsg('');
  };

  // 1. Registration
 const handleRegister = async (e) => {
  e.preventDefault();
  clearMessages();
  try {
    const fullName = `${formData.first_name} ${formData.last_name}`.trim();

    const res = await API.post('users/register/', {
      email: formData.email,
      password: formData.password,
      name: fullName, // Added: combines first_name & last_name to satisfy serializer requirement
      first_name: formData.first_name,
      last_name: formData.last_name
    });
    
    setRegisteredEmail(formData.email);
    if (res.data.otp) setDevOtpCode(res.data.otp);
    setMode('otp');
  } catch (err) {
    const data = err.response?.data;
    if (data && typeof data === 'object') {
      const messages = Object.entries(data)
        .map(([field, msgs]) => `${field.toUpperCase()}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
        .join(' | ');
      setErrorMsg(messages);
    } else {
      setErrorMsg('Registration failed. Check inputs.');
    }
  }
};

  // 2. Register OTP Verification
  async function handleVerifyOTP(e) {
        e.preventDefault();
        clearMessages();
        try {
            await API.post('users/verify_otp/', {
                email: registeredEmail || formData.email,
                code: formData.otp
            });
            alert('Email verified successfully! Please log in now.');
            setMode('login');
        } catch (err) {
            setErrorMsg(JSON.stringify(err.response?.data || 'Invalid OTP code.'));
        }
    }

  // 3. Login
  const handleLogin = async (e) => {
    e.preventDefault();
    clearMessages();
    try {
      const res = await API.post('users/login/', {
        email: formData.email,
        password: formData.password
      });

      if (res.data.access) {
        localStorage.setItem('access_token', res.data.access);
        if (res.data.refresh) localStorage.setItem('refresh_token', res.data.refresh);
        onLoginSuccess(res.data.user || null);
        onClose();
      } else {
        setErrorMsg('Authentication payload did not include an access token.');
      }
    } catch (err) {
      setErrorMsg(JSON.stringify(err.response?.data || 'Invalid credentials or unverified account.'));
    }
  };

  // 4. Request Password Reset OTP (sentOtpForPasswordChange)
  const handleSendPasswordOTP = async (e) => {
    e.preventDefault();
    clearMessages();
    try {
      const res = await API.post('users/sentOtpForPasswordChange/', {
        email: formData.email
      });
      setRegisteredEmail(formData.email);
      setSuccessMsg(res.data.message || 'OTP sent to your email.');
      setMode('reset_password_otp');
    } catch (err) {
      setErrorMsg(JSON.stringify(err.response?.data || 'Failed to send OTP. Ensure email exists.'));
    }
  };

  // 5. Verify Password Reset OTP & Set New Password (ChangePasswordOtpVerification)
  const handleChangePasswordOTP = async (e) => {
    e.preventDefault();
    clearMessages();
    try {
      const res = await API.post('users/ChangePasswordOtpVerification/', {
        email: registeredEmail || formData.email,
        code: formData.otp,
        new_password: formData.new_password
      });
      alert(res.data.message || 'Password reset successfully. Please log in.');
      setMode('login');
    } catch (err) {
      setErrorMsg(JSON.stringify(err.response?.data || 'Password reset failed. Check OTP and input values.'));
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
      <div style={{ backgroundColor: '#fff', width: '400px', borderRadius: '12px', padding: '30px', position: 'relative', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: '15px', right: '15px', border: 'none', background: 'none', cursor: 'pointer' }}>
          <X size={20} />
        </button>

        {errorMsg && (
          <div style={{ backgroundColor: '#fee2e2', color: '#dc2626', padding: '10px', borderRadius: '6px', fontSize: '12px', marginBottom: '15px' }}>
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div style={{ backgroundColor: '#f0fdf4', color: '#166534', padding: '10px', borderRadius: '6px', fontSize: '12px', marginBottom: '15px' }}>
            {successMsg}
          </div>
        )}

        {/* 1. LOGIN FORM */}
        {mode === 'login' && (
          <form onSubmit={handleLogin}>
            <h2 style={{ marginBottom: '20px', color: '#0f172a' }}>Login</h2>
            
            <div style={{ marginBottom: '15px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Email</label>
              <input type="email" name="email" required value={formData.email} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <div style={{ marginBottom: '10px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Password</label>
              <input type="password" name="password" required value={formData.password} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <div style={{ textAlign: 'right', marginBottom: '20px' }}>
              <span onClick={() => { clearMessages(); setMode('forgot_password'); }} style={{ fontSize: '12px', color: '#059669', cursor: 'pointer', fontWeight: 'bold' }}>
                Forgot Password?
              </span>
            </div>

            <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Sign In
            </button>

            <p style={{ fontSize: '13px', textAlign: 'center', marginTop: '15px' }}>
              Don't have an account? <span onClick={() => { clearMessages(); setMode('register'); }} style={{ color: '#059669', fontWeight: 'bold', cursor: 'pointer' }}>Sign Up</span>
            </p>
          </form>
        )}

        {/* 2. REGISTER FORM */}
        {mode === 'register' && (
          <form onSubmit={handleRegister}>
            <h2 style={{ marginBottom: '20px', color: '#0f172a' }}>Create Account</h2>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 'bold' }}>First Name</label>
                <input type="text" name="first_name" required value={formData.first_name} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Last Name</label>
                <input type="text" name="last_name" required value={formData.last_name} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Email Address</label>
              <input type="email" name="email" required value={formData.email} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Password</label>
              <input type="password" name="password" required value={formData.password} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Register
            </button>

            <p style={{ fontSize: '13px', textAlign: 'center', marginTop: '15px' }}>
              Already registered? <span onClick={() => { clearMessages(); setMode('login'); }} style={{ color: '#059669', fontWeight: 'bold', cursor: 'pointer' }}>Login</span>
            </p>
          </form>
        )}

        {/* 3. REGISTER OTP VERIFICATION FORM */}
        {mode === 'otp' && (
          <form onSubmit={handleVerifyOTP}>
            <h2 style={{ marginBottom: '10px', color: '#0f172a' }}>Verify Your Email</h2>
            <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '15px' }}>
              An OTP code was generated for <strong>{registeredEmail}</strong>.
            </p>

            {devOtpCode && (
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', padding: '8px', borderRadius: '6px', fontSize: '12px', color: '#166534', marginBottom: '15px' }}>
                Testing OTP Code: <strong>{devOtpCode}</strong>
              </div>
            )}

            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Enter 6-Digit OTP</label>
              <input type="text" name="otp" required value={formData.otp} onChange={handleChange} placeholder="123456" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px', textAlign: 'center', letterSpacing: '4px', fontSize: '18px' }} />
            </div>

            <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Verify OTP
            </button>
          </form>
        )}

        {/* 4. REQUEST PASSWORD RESET OTP FORM */}
        {mode === 'forgot_password' && (
          <form onSubmit={handleSendPasswordOTP}>
            <h2 style={{ marginBottom: '10px', color: '#0f172a' }}>Reset Password</h2>
            <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '15px' }}>
              Enter your email to receive a password reset OTP code.
            </p>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Email Address</label>
              <input type="email" name="email" required value={formData.email} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Send Reset OTP
            </button>

            <p style={{ fontSize: '13px', textAlign: 'center', marginTop: '15px' }}>
              Remember password? <span onClick={() => { clearMessages(); setMode('login'); }} style={{ color: '#059669', fontWeight: 'bold', cursor: 'pointer' }}>Login</span>
            </p>
          </form>
        )}

        {/* 5. VERIFY PASSWORD RESET OTP & CHANGE PASSWORD */}
        {mode === 'reset_password_otp' && (
          <form onSubmit={handleChangePasswordOTP}>
            <h2 style={{ marginBottom: '10px', color: '#0f172a' }}>Set New Password</h2>
            <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '15px' }}>
              Enter the OTP sent to <strong>{registeredEmail || formData.email}</strong> and your new password.
            </p>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Enter OTP</label>
              <input type="text" name="otp" required value={formData.otp} onChange={handleChange} placeholder="123456" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px', textAlign: 'center', letterSpacing: '4px', fontSize: '16px' }} />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '12px', fontWeight: 'bold' }}>New Password</label>
              <input type="password" name="new_password" required value={formData.new_password} onChange={handleChange} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', marginTop: '4px' }} />
            </div>

            <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Reset Password
            </button>
          </form>
        )}
      </div>
    </div>
  );
}