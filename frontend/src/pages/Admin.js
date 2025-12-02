import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { booksAPI, authorsAPI, publishersAPI, reviewsAPI } from '../services/api';
import './Admin.css';

const Admin = () => {
  const { t } = useTranslation();
  const { isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('books');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({});
  const [editingId, setEditingId] = useState(null);

  const tabs = [
    { key: 'books', label: t('admin.books') },
    { key: 'authors', label: t('admin.authors') },
    { key: 'publishers', label: t('admin.publishers') },
    { key: 'reviews', label: t('admin.reviews') }
  ];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        let response;
        switch (activeTab) {
          case 'books':
            response = await booksAPI.search({ limit: 50 });
            setData(response.data.books);
            break;
          case 'authors':
            response = await authorsAPI.getAll({ limit: 50 });
            setData(response.data.authors);
            break;
          case 'publishers':
            response = await publishersAPI.getAll({ limit: 50 });
            setData(response.data.publishers);
            break;
          case 'reviews':
            response = await reviewsAPI.getPending({ limit: 50 });
            setData(response.data.reviews);
            break;
          default:
            setData([]);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    refreshData();
  }, [activeTab]);

  const refreshData = async () => {
    setLoading(true);
    try {
      let response;
      switch (activeTab) {
        case 'books':
          response = await booksAPI.search({ limit: 50 });
          setData(response.data.books);
          break;
        case 'authors':
          response = await authorsAPI.getAll({ limit: 50 });
          setData(response.data.authors);
          break;
        case 'publishers':
          response = await publishersAPI.getAll({ limit: 50 });
          setData(response.data.publishers);
          break;
        case 'reviews':
          response = await reviewsAPI.getPending({ limit: 50 });
          setData(response.data.reviews);
          break;
        default:
          setData([]);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingId(null);
    setFormData({});
    setShowForm(true);
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setFormData(item);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      switch (activeTab) {
        case 'books':
          await booksAPI.deleteBook(id);
          break;
        case 'authors':
          await authorsAPI.delete(id);
          break;
        case 'publishers':
          await publishersAPI.delete(id);
          break;
        default:
          break;
      }
      refreshData();
    } catch (err) {
      alert('Error deleting item');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      switch (activeTab) {
        case 'books':
          if (editingId) {
            await booksAPI.updateBook(editingId, formData);
          } else {
            await booksAPI.createBook(formData);
          }
          break;
        case 'authors':
          if (editingId) {
            await authorsAPI.update(editingId, formData);
          } else {
            await authorsAPI.create(formData);
          }
          break;
        case 'publishers':
          if (editingId) {
            await publishersAPI.update(editingId, formData);
          } else {
            await publishersAPI.create(formData);
          }
          break;
        default:
          break;
      }
      setShowForm(false);
      refreshData();
    } catch (err) {
      alert('Error saving item');
    }
  };

  const handleApproveReview = async (id) => {
    try {
      await reviewsAPI.approve(id);
      refreshData();
    } catch (err) {
      alert('Error approving review');
    }
  };

  const handleRejectReview = async (id) => {
    try {
      await reviewsAPI.reject(id);
      refreshData();
    } catch (err) {
      alert('Error rejecting review');
    }
  };

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  const renderForm = () => {
    switch (activeTab) {
      case 'books':
        return (
          <>
            <input
              type="text"
              placeholder="Title (English)"
              value={formData.title || ''}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Title (Thai)"
              value={formData.title_th || ''}
              onChange={(e) => setFormData({ ...formData, title_th: e.target.value })}
            />
            <textarea
              placeholder="Description (English)"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
            />
            <textarea
              placeholder="Description (Thai)"
              value={formData.description_th || ''}
              onChange={(e) => setFormData({ ...formData, description_th: e.target.value })}
              rows={3}
            />
            <input
              type="url"
              placeholder="Cover Image URL"
              value={formData.cover_image_url || ''}
              onChange={(e) => setFormData({ ...formData, cover_image_url: e.target.value })}
            />
            <select
              value={formData.type || 'manga'}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            >
              <option value="manga">Manga</option>
              <option value="novel">Novel</option>
              <option value="light_novel">Light Novel</option>
              <option value="manhwa">Manhwa</option>
              <option value="manhua">Manhua</option>
            </select>
            <select
              value={formData.status || 'ongoing'}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <option value="ongoing">Ongoing</option>
              <option value="completed">Completed</option>
              <option value="hiatus">Hiatus</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <input
              type="number"
              placeholder="Publication Year"
              value={formData.publication_year || ''}
              onChange={(e) => setFormData({ ...formData, publication_year: parseInt(e.target.value) })}
            />
          </>
        );
      case 'authors':
        return (
          <>
            <input
              type="text"
              placeholder="Name (English)"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Name (Thai)"
              value={formData.name_th || ''}
              onChange={(e) => setFormData({ ...formData, name_th: e.target.value })}
            />
            <textarea
              placeholder="Biography (English)"
              value={formData.biography || ''}
              onChange={(e) => setFormData({ ...formData, biography: e.target.value })}
              rows={3}
            />
            <textarea
              placeholder="Biography (Thai)"
              value={formData.biography_th || ''}
              onChange={(e) => setFormData({ ...formData, biography_th: e.target.value })}
              rows={3}
            />
          </>
        );
      case 'publishers':
        return (
          <>
            <input
              type="text"
              placeholder="Name (English)"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Name (Thai)"
              value={formData.name_th || ''}
              onChange={(e) => setFormData({ ...formData, name_th: e.target.value })}
            />
            <textarea
              placeholder="Description"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
            />
            <input
              type="url"
              placeholder="Website URL"
              value={formData.website_url || ''}
              onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
            />
          </>
        );
      default:
        return null;
    }
  };

  const renderTable = () => {
    if (loading) return <div className="loading">{t('common.loading')}</div>;
    if (data.length === 0) return <p>No data found</p>;

    if (activeTab === 'reviews') {
      return (
        <div className="reviews-list">
          {data.map((review) => (
            <div key={review.id} className="review-item">
              <div className="review-info">
                <strong>{review.username}</strong> reviewed <em>{review.book_title}</em>
                <div className="review-rating">{'⭐'.repeat(review.rating)}</div>
                <p>{review.content}</p>
              </div>
              <div className="review-actions">
                <button className="approve-btn" onClick={() => handleApproveReview(review.id)}>
                  ✓ Approve
                </button>
                <button className="reject-btn" onClick={() => handleRejectReview(review.id)}>
                  ✕ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return (
      <table className="data-table">
        <thead>
          <tr>
            <th>Name/Title</th>
            {activeTab === 'books' && <th>Type</th>}
            {activeTab === 'books' && <th>Status</th>}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id}>
              <td>{item.title || item.name}</td>
              {activeTab === 'books' && <td>{item.type}</td>}
              {activeTab === 'books' && <td>{item.status}</td>}
              <td>
                <button className="edit-btn" onClick={() => handleEdit(item)}>
                  {t('admin.edit')}
                </button>
                <button className="delete-btn" onClick={() => handleDelete(item.id)}>
                  {t('admin.delete')}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="admin-page">
      <h1>{t('admin.dashboard')}</h1>

      <div className="admin-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => {
              setActiveTab(tab.key);
              setShowForm(false);
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="admin-content">
        {activeTab !== 'reviews' && (
          <button className="add-btn" onClick={handleAdd}>
            + {t('admin.add')}
          </button>
        )}

        {showForm && (
          <form className="admin-form" onSubmit={handleSubmit}>
            <h3>{editingId ? t('admin.edit') : t('admin.add')}</h3>
            {renderForm()}
            <div className="form-actions">
              <button type="submit" className="save-btn">{t('common.save')}</button>
              <button type="button" className="cancel-btn" onClick={() => setShowForm(false)}>
                {t('common.cancel')}
              </button>
            </div>
          </form>
        )}

        {renderTable()}
      </div>
    </div>
  );
};

export default Admin;
