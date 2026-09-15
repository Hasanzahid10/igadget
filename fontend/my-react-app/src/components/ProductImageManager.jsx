import React, { useState, useEffect } from 'react';
import API from '../api/axios';
import { Upload, Star, Trash2, Image as ImageIcon, AlertCircle } from 'lucide-react';

export default function ProductImageManager({ productId, productName, onClose }) {
  const [images, setImages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isPrimary, setIsPrimary] = useState(false);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (productId) {
      fetchProductImages();
    }
  }, [productId]);

  // Fetch images for the specific product
  const fetchProductImages = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      // Queries AdminProductImageViewSet filtered by product
      const res = await API.get(`admin/product-images/?product=${productId}`);
      setImages(res.data.results || res.data);
    } catch (err) {
      setErrorMsg('Failed to load product images.');
    } finally {
      setLoading(false);
    }
  };

  // 1. Upload New Image (POST /api/admin/product-images/)
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMsg('Please select an image file to upload.');
      return;
    }

    setUploading(true);
    setErrorMsg('');

    // Construct Multipart Form Data payload
    const formData = new FormData();
    formData.append('product', productId);
    formData.append('image', selectedFile);
    formData.append('is_primary', isPrimary);

    try {
      await API.post('admin/product-images/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSelectedFile(null);
      setIsPrimary(false);
      fetchProductImages(); // Refresh image list
    } catch (err) {
      setErrorMsg(JSON.stringify(err.response?.data || 'Failed to upload image.'));
    } finally {
      setUploading(false);
    }
  };

  // 2. Set as Primary Image (PATCH /api/admin/product-images/{id}/)
  const handleSetPrimary = async (imageId) => {
    try {
      await API.patch(`admin/product-images/${imageId}/`, { is_primary: true });
      fetchProductImages();
    } catch (err) {
      alert('Failed to set primary image.');
    }
  };

  // 3. Delete Image (DELETE /api/admin/product-images/{id}/)
  const handleDeleteImage = async (imageId) => {
    if (!window.confirm('Are you sure you want to delete this image?')) return;
    try {
      await API.delete(`admin/product-images/${imageId}/`);
      fetchProductImages();
    } catch (err) {
      alert('Failed to delete image.');
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1100 }}>
      <div style={{ backgroundColor: '#fff', width: '650px', maxHeight: '85vh', borderRadius: '12px', padding: '25px', overflowY: 'auto', position: 'relative', boxShadow: '0 10px 25px rgba(0,0,0,0.15)' }}>
        
        {/* HEADER */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '18px', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ImageIcon size={20} color="#059669" /> Manage Images: {productName || `#${productId}`}
          </h2>
          <button onClick={onClose} style={{ border: 'none', background: 'none', fontSize: '18px', cursor: 'pointer', color: '#64748b' }}>✕</button>
        </div>

        {errorMsg && (
          <div style={{ backgroundColor: '#fee2e2', color: '#dc2626', padding: '10px', borderRadius: '6px', fontSize: '12px', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle size={14} /> {errorMsg}
          </div>
        )}

        {/* UPLOAD FORM */}
        <form onSubmit={handleUpload} style={{ backgroundColor: '#f8fafc', padding: '15px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '20px' }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#334155' }}>Upload New Image</h4>
          
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <input 
              type="file" 
              accept="image/*" 
              onChange={(e) => setSelectedFile(e.target.files[0])} 
              style={{ fontSize: '12px' }}
            />
            
            <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={isPrimary} 
                onChange={(e) => setIsPrimary(e.target.checked)} 
              />
              Set as Primary
            </label>

            <button 
              type="submit" 
              disabled={uploading} 
              style={{ backgroundColor: '#059669', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', marginLeft: 'auto' }}
            >
              <Upload size={14} /> {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>

        {/* EXISTING IMAGES GRID */}
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#334155' }}>Existing Gallery</h4>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px', fontSize: '13px', color: '#64748b' }}>Loading images...</div>
        ) : images.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', fontSize: '13px', color: '#64748b', border: '1px dashed #cbd5e1', borderRadius: '6px' }}>No images uploaded yet.</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
            {images.map((img) => (
              <div key={img.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '8px', position: 'relative', backgroundColor: '#fff' }}>
                <img 
                  src={img.image} 
                  alt="Product" 
                  style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '6px' }} 
                />
                
                {/* Primary Tag */}
                {img.is_primary && (
                  <span style={{ position: 'absolute', top: '12px', left: '12px', backgroundColor: '#059669', color: '#fff', fontSize: '10px', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <Star size={10} fill="#fff" /> Primary
                  </span>
                )}

                {/* Actions */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                  {!img.is_primary && (
                    <button 
                      onClick={() => handleSetPrimary(img.id)}
                      style={{ backgroundColor: '#f1f5f9', border: '1px solid #cbd5e1', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                    >
                      Make Primary
                    </button>
                  )}
                  
                  <button 
                    onClick={() => handleDeleteImage(img.id)}
                    style={{ backgroundColor: '#fee2e2', color: '#dc2626', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer', marginLeft: 'auto' }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}