import React, { useState, useEffect } from 'react';
import { 
  Search, Heart, ShoppingBag, Phone, Truck, ShieldCheck, 
  Award, Headphones, ArrowRight, X, CheckCircle 
} from 'lucide-react';
import API from '../api/axios'; // Import configured Axios instance

export default function Home() {
  // State from Django API
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Search & Filter State
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Cart & Order Modal State
  const [cart, setCart] = useState([]);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(null);

  // Form State matching Django Order Model
  const [orderForm, setOrderForm] = useState({
    phone_number: '',
    address_line: '',
    city: 'Dhaka',
    postal_code: ''
  });

  // Fetch Data from Django Backend
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [catRes, prodRes] = await Promise.all([
        API.get('catalog/categories/'),
        API.get('catalog/products/?is_deal=true') // Get Top Deals
      ]);
      setCategories(catRes.data.results || catRes.data);
      setProducts(prodRes.data.results || prodRes.data);
    } catch (err) {
      console.error("Failed to load catalog data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Add Product to Cart
  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  // Calculate Order Total
  const cartTotal = cart.reduce((sum, item) => sum + ((item.discount_price || item.price) * item.quantity), 0);

  // Submit Order to Django /api/orders/
  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    if (!orderForm.phone_number || !orderForm.address_line) {
      alert("Please provide phone number and delivery address.");
      return;
    }

    const payload = {
      phone_number: orderForm.phone_number,
      shipping_fee: 60.00,
      total_amount: (cartTotal + 60.00).toFixed(2),
      shipping_address: {
        address: orderForm.address_line,
        city: orderForm.city,
        postal_code: orderForm.postal_code
      },
      items: cart.map(item => ({
        product: item.id,
        quantity: item.quantity,
        unit_price: item.discount_price || item.price
      }))
    };

    try {
      const res = await API.post('orders/', payload);
      setOrderSuccess(res.data.order_number || "ORDER-SUCCESS");
      setCart([]); // Clear Cart
    } catch (err) {
      alert("Order placement failed. Ensure you are logged in.");
      console.error(err);
    }
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', paddingBottom: '50px' }}>
      
      {/* 1. TOP BAR */}
      <div style={{ backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0', fontSize: '12px', padding: '6px 40px', display: 'flex', justifyContent: 'space-between', color: '#64748b' }}>
        <span>🚚 Free Delivery on orders over ৳999</span>
        <div style={{ display: 'flex', gap: '20px' }}>
          <span>Help & Support</span>
          <span>Track Order</span>
          <span>English</span>
        </div>
      </div>

      {/* 2. MAIN HEADER */}
      <header style={{ backgroundColor: '#fff', padding: '15px 40px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', sticky: 'top' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '24px', fontWeight: 'bold', color: '#059669' }}>
          <ShoppingBag size={28} /> ShopEase
        </div>

        {/* Search Bar */}
        <div style={{ display: 'flex', width: '50%', border: '2px solid #059669', borderRadius: '8px', overflow: 'hidden' }}>
          <select 
            onChange={(e) => setSelectedCategory(e.target.value)} 
            style={{ padding: '10px', border: 'none', backgroundColor: '#f8fafc', borderRight: '1px solid #cbd5e1', outline: 'none' }}
          >
            <option value="">All Categories</option>
            {categories.map(c => <option key={c.id} value={c.slug}>{c.name}</option>)}
          </select>
          <input 
            type="text" 
            placeholder="Search for products..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: 1, border: 'none', padding: '10px', outline: 'none' }} 
          />
          <button style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '0 20px', cursor: 'pointer' }}>
            <Search size={18} />
          </button>
        </div>

        {/* Right Nav Icons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '25px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
            <Heart size={20} /> <span style={{ fontSize: '14px' }}>Wishlist</span>
          </div>
          <div 
            onClick={() => setIsCheckoutOpen(true)}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', position: 'relative' }}
          >
            <ShoppingBag size={20} />
            <span style={{ fontSize: '14px' }}>Cart</span>
            {cart.length > 0 && (
              <span style={{ position: 'absolute', top: '-8px', right: '-12px', backgroundColor: '#059669', color: '#fff', fontSize: '11px', fontWeight: 'bold', borderRadius: '50%', width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {cart.reduce((a, b) => a + b.quantity, 0)}
              </span>
            )}
          </div>
        </div>
      </header>

      {/* 3. HERO BANNER */}
      <section style={{ margin: '20px 40px', backgroundColor: '#e2f1e8', borderRadius: '16px', padding: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ maxWidth: '500px' }}>
          <span style={{ color: '#059669', fontWeight: 'bold', fontSize: '12px', letterSpacing: '1px' }}>NEW ARRIVALS</span>
          <h1 style={{ fontSize: '38px', color: '#0f172a', margin: '10px 0' }}>Discover the Best Products for You</h1>
          <p style={{ color: '#475569', marginBottom: '20px' }}>Top quality products at the best prices. Shop smart, save more!</p>
          <div style={{ display: 'flex', gap: '15px' }}>
            <button style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>Shop Now</button>
            <button style={{ backgroundColor: '#fff', color: '#0f172a', border: '1px solid #cbd5e1', padding: '12px 24px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>Explore Deals</button>
          </div>
        </div>
        <div style={{ position: 'relative' }}>
          <img src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500" alt="Headphones Banner" style={{ width: '380px', borderRadius: '12px' }} />
          <div style={{ position: 'absolute', top: '10px', right: '10px', backgroundColor: '#059669', color: '#fff', borderRadius: '50%', padding: '15px', fontWeight: 'bold', textAlign: 'center' }}>
            UP TO<br/><span style={{ fontSize: '18px' }}>50%</span><br/>OFF
          </div>
        </div>
      </section>

      {/* 4. VALUE PROPOSITION BADGES */}
      <section style={{ margin: '0 40px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #f1f5f9' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Truck color="#059669" size={32} />
          <div><h4 style={{ margin: 0 }}>Free Delivery</h4><span style={{ fontSize: '12px', color: '#64748b' }}>On orders over ৳999</span></div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <ShieldCheck color="#059669" size={32} />
          <div><h4 style={{ margin: 0 }}>Secure Payment</h4><span style={{ fontSize: '12px', color: '#64748b' }}>100% secure payment</span></div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Award color="#059669" size={32} />
          <div><h4 style={{ margin: 0 }}>Best Quality</h4><span style={{ fontSize: '12px', color: '#64748b' }}>Quality products</span></div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Headphones color="#059669" size={32} />
          <div><h4 style={{ margin: 0 }}>24/7 Support</h4><span style={{ fontSize: '12px', color: '#64748b' }}>Dedicated support</span></div>
        </div>
      </section>

      {/* 5. SHOP BY CATEGORIES */}
      <section style={{ margin: '40px 40px 20px 40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2>Shop by Categories</h2>
          <span style={{ color: '#059669', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }}>View All Categories</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: '15px' }}>
          {categories.map((cat) => (
            <div key={cat.id} style={{ backgroundColor: '#fff', borderRadius: '50%', padding: '20px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.02)', cursor: 'pointer', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '24px', marginBottom: '5px' }}>📱</div>
              <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#334155' }}>{cat.name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* 6. TOP DEALS PRODUCTS GRID */}
      <section style={{ margin: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2>Top Deals</h2>
          <span style={{ color: '#059669', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }}>View All Deals</span>
        </div>

        {loading ? (
          <p>Loading catalog products...</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '15px' }}>
            {products.map((prod) => (
              <div key={prod.id} style={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px', position: 'relative' }}>
                <img 
                  src={prod.images && prod.images.length > 0 ? prod.images[0].images : 'https://via.placeholder.com/150'} 
                  alt={prod.title} 
                  style={{ width: '100%', height: '120px', objectFit: 'contain', marginBottom: '10px' }} 
                />
                <h4 style={{ fontSize: '13px', margin: '5px 0', height: '36px', overflow: 'hidden' }}>{prod.title}</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '15px', fontWeight: 'bold', color: '#059669' }}>৳{prod.discount_price || prod.price}</span>
                  {prod.discount_price && (
                    <span style={{ fontSize: '11px', color: '#94a3b8', textDecoration: 'line-through' }}>৳{prod.price}</span>
                  )}
                </div>
                <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '10px', backgroundColor: '#fee2e2', color: '#ef4444', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>
                    -{prod.discount_percentage}%
                  </span>
                  <button 
                    onClick={() => addToCart(prod)}
                    style={{ backgroundColor: '#e2f1e8', color: '#059669', border: 'none', padding: '6px', borderRadius: '50%', cursor: 'pointer' }}
                  >
                    <ShoppingBag size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* 7. CHECKOUT / ORDER MODAL */}
      {isCheckoutOpen && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#fff', borderRadius: '12px', width: '450px', padding: '25px', position: 'relative' }}>
            <button onClick={() => setIsCheckoutOpen(false)} style={{ position: 'absolute', top: '15px', right: '15px', border: 'none', background: 'none', cursor: 'pointer' }}><X size={20}/></button>
            
            {orderSuccess ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <CheckCircle size={50} color="#059669" style={{ marginBottom: '10px' }} />
                <h3>Order Placed Successfully!</h3>
                <p>Order Reference: <strong>{orderSuccess}</strong></p>
                <p style={{ fontSize: '12px', color: '#64748b' }}>Our verification team will call your phone number before shipping.</p>
                <button onClick={() => { setIsCheckoutOpen(false); setOrderSuccess(null); }} style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '6px', marginTop: '15px', cursor: 'pointer' }}>Close</button>
              </div>
            ) : (
              <form onSubmit={handlePlaceOrder}>
                <h3>Order Checkout</h3>
                <div style={{ maxHeight: '150px', overflowY: 'auto', borderBottom: '1px solid #e2e8f0', marginBottom: '15px' }}>
                  {cart.map(item => (
                    <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '8px' }}>
                      <span>{item.quantity}x {item.title}</span>
                      <span>৳{(item.discount_price || item.price) * item.quantity}</span>
                    </div>
                  ))}
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Phone Number (For Call Verification)</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="01700000000" 
                    value={orderForm.phone_number} 
                    onChange={e => setOrderForm({...orderForm, phone_number: e.target.value})}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', marginTop: '4px' }}
                  />
                </div>

                <div style={{ marginBottom: '15px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 'bold' }}>Delivery Address</label>
                  <textarea 
                    required 
                    placeholder="House, Street, Area details..." 
                    value={orderForm.address_line} 
                    onChange={e => setOrderForm({...orderForm, address_line: e.target.value})}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', marginTop: '4px' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', marginBottom: '15px' }}>
                  <span>Total (Incl. Shipping ৳60):</span>
                  <span>৳{(cartTotal + 60).toFixed(2)}</span>
                </div>

                <button type="submit" style={{ width: '100%', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
                  Confirm & Place Order
                </button>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}