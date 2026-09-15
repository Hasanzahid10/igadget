import React, { useState, useEffect } from 'react';
import API from '../api/axios';
import { Package, ShoppingBag, FolderTree, PhoneCall, CheckCircle, Edit, RefreshCw } from 'lucide-react';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('orders'); // 'orders' | 'products' | 'categories'
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedProductForImages, setSelectedProductForImages] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Price Modification State
  const [editingPriceId, setEditingPriceId] = useState(null);
  const [priceForm, setPriceForm] = useState({ price: '', discount_price: '' });

  useEffect(() => {
    fetchDashboardData();
  }, [activeTab]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'orders') {
        const res = await API.get('admin/orders/');
        setOrders(res.data.results || res.data);
      } else if (activeTab === 'products') {
        const res = await API.get('admin/products/');
        setProducts(res.data.results || res.data);
      } else if (activeTab === 'categories') {
        const res = await API.get('admin/categories/');
        setCategories(res.data.results || res.data);
      }
    } catch (err) {
      console.error("Error fetching admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  // 1. Confirm Order by Phone Call (POST /api/admin/orders/{id}/confirm_by_call/)
  const handleConfirmByCall = async (orderId) => {
    try {
      const res = await API.post(`admin/orders/${orderId}/confirm_by_call/`);
      alert(res.data.message);
      fetchDashboardData();
    } catch (err) {
      alert("Failed to confirm order.");
    }
  };

  // 2. Update Shipping Status (POST /api/admin/orders/{id}/update_status/)
  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      const res = await API.post(`admin/orders/${orderId}/update_status/`, { status: newStatus });
      alert(res.data.message);
      fetchDashboardData();
    } catch (err) {
      alert("Failed to update status.");
    }
  };

  // 3. Update Product Price and Discount (PATCH /api/admin/products/{id}/update_price_and_discount/)
  const handlePriceUpdate = async (productId) => {
    try {
      await API.patch(`admin/products/${productId}/update_price_and_discount/`, priceForm);
      setEditingPriceId(null);
      fetchDashboardData();
    } catch (err) {
      alert("Failed to update price.");
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '30px auto', padding: '0 20px', fontFamily: 'Inter, sans-serif' }}>
      
      {/* HEADER & NAVIGATION TABS */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
        <h1 style={{ margin: 0, fontSize: '24px', color: '#0f172a' }}>Admin Control Center</h1>
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => setActiveTab('orders')}
            style={{ padding: '8px 16px', borderRadius: '6px', border: 'none', backgroundColor: activeTab === 'orders' ? '#0f172a' : '#e2e8f0', color: activeTab === 'orders' ? '#fff' : '#334155', cursor: 'pointer', fontWeight: 'bold' }}
          >
            <ShoppingBag size={14} style={{ marginRight: '6px' }} /> Orders
          </button>
          
          <button 
            onClick={() => setActiveTab('products')}
            style={{ padding: '8px 16px', borderRadius: '6px', border: 'none', backgroundColor: activeTab === 'products' ? '#0f172a' : '#e2e8f0', color: activeTab === 'products' ? '#fff' : '#334155', cursor: 'pointer', fontWeight: 'bold' }}
          >
            <Package size={14} style={{ marginRight: '6px' }} /> Products
          </button>
          <button 
            onClick={() => setSelectedProductForImages(prod)}
            style={{ backgroundColor: '#0f172a', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
            >Gallery
           </button>

          <button 
            onClick={() => setActiveTab('categories')}
            style={{ padding: '8px 16px', borderRadius: '6px', border: 'none', backgroundColor: activeTab === 'categories' ? '#0f172a' : '#e2e8f0', color: activeTab === 'categories' ? '#fff' : '#334155', cursor: 'pointer', fontWeight: 'bold' }}
          >
            <FolderTree size={14} style={{ marginRight: '6px' }} /> Categories
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>Loading control panel...</div>
      ) : (
        <>
          {/* ORDERS TAB */}
          {activeTab === 'orders' && (
            <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                <thead style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <tr>
                    <th style={{ padding: '12px' }}>Order No</th>
                    <th style={{ padding: '12px' }}>Customer Email</th>
                    <th style={{ padding: '12px' }}>Phone</th>
                    <th style={{ padding: '12px' }}>Status</th>
                    <th style={{ padding: '12px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '12px', fontWeight: 'bold' }}>{order.order_number || order.order_numbre || `#${order.id}`}</td>
                      <td style={{ padding: '12px' }}>{order.user?.email || 'Guest'}</td>
                      <td style={{ padding: '12px' }}>{order.phone_number || 'N/A'}</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ padding: '4px 8px', borderRadius: '4px', fontSize: '12px', backgroundColor: order.status === 'delivered' ? '#dcfce7' : '#fef3c7', color: order.status === 'delivered' ? '#166534' : '#92400e', fontWeight: 'bold' }}>
                          {order.status}
                        </span>
                      </td>
                      <td style={{ padding: '12px', display: 'flex', gap: '8px' }}>
                        <button 
                          onClick={() => handleConfirmByCall(order.id)}
                          style={{ backgroundColor: '#0284c7', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          <PhoneCall size={12} /> Confirm Call
                        </button>

                        <select 
                          value={order.status} 
                          onChange={(e) => handleUpdateStatus(order.id, e.target.value)}
                          style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '12px' }}
                        >
                          <option value="pending">Pending</option>
                          <option value="processing">Processing</option>
                          <option value="shipped">Shipped</option>
                          <option value="delivered">Delivered</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* PRODUCTS TAB */}
          {activeTab === 'products' && (
            <div style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                <thead style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <tr>
                    <th style={{ padding: '12px' }}>Title</th>
                    <th style={{ padding: '12px' }}>Price</th>
                    <th style={{ padding: '12px' }}>Discount Price</th>
                    <th style={{ padding: '12px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((prod) => (
                    <tr key={prod.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '12px', fontWeight: 'bold' }}>{prod.title || prod.name}</td>
                      <td style={{ padding: '12px' }}>${prod.price}</td>
                      <td style={{ padding: '12px' }}>{prod.discount_price ? `$${prod.discount_price}` : 'None'}</td>
                      <td style={{ padding: '12px' }}>
                        {editingPriceId === prod.id ? (
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <input 
                              type="number" 
                              placeholder="Price" 
                              value={priceForm.price} 
                              onChange={(e) => setPriceForm({...priceForm, price: e.target.value})} 
                              style={{ width: '70px', padding: '4px' }}
                            />
                            <input 
                              type="number" 
                              placeholder="Discount" 
                              value={priceForm.discount_price} 
                              onChange={(e) => setPriceForm({...priceForm, discount_price: e.target.value})} 
                              style={{ width: '70px', padding: '4px' }}
                            />
                            <button onClick={() => handlePriceUpdate(prod.id)} style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}>Save</button>
                          </div>
                        ) : (
                          <button 
                            onClick={() => { setEditingPriceId(prod.id); setPriceForm({ price: prod.price, discount_price: prod.discount_price || '' }); }}
                            style={{ backgroundColor: '#f1f5f9', border: '1px solid #cbd5e1', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
                          >
                            <Edit size={12} /> Edit Price
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* CATEGORIES TAB */}
          {activeTab === 'categories' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
              {categories.map((cat) => (
                <div key={cat.id} style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '15px' }}>
                  <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>{cat.name}</h3>
                  <p style={{ margin: 0, color: '#64748b', fontSize: '12px' }}>ID: {cat.id}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}

    </div>
  );
}