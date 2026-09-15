import React, { useState, useEffect } from 'react';
import API from '../api/axios';
import { User, MapPin, Trash2, Plus } from 'lucide-react';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Address Form State
  const [newAddress, setNewAddress] = useState({
    street_address: '',
    city: '',
    postal_code: '',
    country: 'Bangladesh'
  });

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const [userRes, addrRes] = await Promise.all([
        API.get('users/me/'),
        API.get('users/address/')
      ]);
      setProfile(userRes.data);
      setAddresses(addrRes.data);
    } catch (err) {
      console.error("Error fetching profile:", err);
    } finally {
      setLoading(false);
    }
  };

  // Add Address
  const handleAddAddress = async (e) => {
    e.preventDefault();
    try {
      await API.post('users/address/', newAddress);
      setNewAddress({ street_address: '', city: '', postal_code: '', country: 'Bangladesh' });
      fetchProfileData(); // Refresh address list
    } catch (err) {
      alert("Failed to add address.");
    }
  };

  // Delete Address
  const handleDeleteAddress = async (id) => {
    try {
      await API.delete('users/address/', { data: { id } });
      fetchProfileData();
    } catch (err) {
      alert("Failed to delete address.");
    }
  };

  if (loading) return <div style={{ padding: '40px' }}>Loading profile information...</div>;

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px', fontFamily: 'Inter, sans-serif' }}>
      
      {/* PROFILE DETAILS */}
      <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '25px', border: '1px solid #e2e8f0', marginBottom: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
          <User size={32} color="#059669" />
          <div>
            <h2 style={{ margin: 0 }}>{profile?.first_name} {profile?.last_name}</h2>
            <span style={{ color: '#64748b', fontSize: '14px' }}>{profile?.email}</span>
          </div>
        </div>
      </div>

      {/* ADDRESSES SECTION */}
      <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '25px', border: '1px solid #e2e8f0' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: 0 }}>
          <MapPin size={20} color="#059669" /> Delivery Addresses
        </h3>

        {/* Existing Addresses */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginBottom: '25px' }}>
          {addresses.map((addr) => (
            <div key={addr.id} style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '15px', position: 'relative' }}>
              <button 
                onClick={() => handleDeleteAddress(addr.id)} 
                style={{ position: 'absolute', top: '10px', right: '10px', border: 'none', background: 'none', color: '#ef4444', cursor: 'pointer' }}
              >
                <Trash2 size={16} />
              </button>
              <p style={{ margin: '0 0 5px 0', fontWeight: 'bold', fontSize: '14px' }}>{addr.street_address}</p>
              <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>{addr.city}, {addr.postal_code}</p>
            </div>
          ))}
        </div>

        {/* Add Address Form */}
        <form onSubmit={handleAddAddress} style={{ borderTop: '1px solid #f1f5f9', paddingTop: '20px' }}>
          <h4 style={{ margin: '0 0 15px 0' }}>Add New Address</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '10px' }}>
            <input type="text" placeholder="Street Address" required value={newAddress.street_address} onChange={e => setNewAddress({...newAddress, street_address: e.target.value})} style={{ padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px' }} />
            <input type="text" placeholder="City" required value={newAddress.city} onChange={e => setNewAddress({...newAddress, city: e.target.value})} style={{ padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px' }} />
            <input type="text" placeholder="Postal Code" required value={newAddress.postal_code} onChange={e => setNewAddress({...newAddress, postal_code: e.target.value})} style={{ padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px' }} />
          </div>
          <button type="submit" style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
            Save Address
          </button>
        </form>
      </div>

    </div>
  );
}