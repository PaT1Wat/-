'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/contexts/I18nContext';
import { useAuth } from '@/contexts/AuthContext';
import { booksAPI, authorsAPI, publishersAPI, reviewsAPI } from '@/lib/api';
import type { Book, Author, Publisher, Review } from '@/lib/types';

type TabKey = 'books' | 'authors' | 'publishers' | 'reviews';
type DataItem = Book | Author | Publisher | Review;

export default function AdminPage() {
  const { t } = useI18n();
  const { isAdmin } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabKey>('books');
  const [data, setData] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [editingId, setEditingId] = useState<string | null>(null);

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'books', label: t('admin.books') },
    { key: 'authors', label: t('admin.authors') },
    { key: 'publishers', label: t('admin.publishers') },
    { key: 'reviews', label: t('admin.reviews') }
  ];

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
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAdmin) {
      router.push('/');
      return;
    }
    refreshData();
  }, [activeTab, isAdmin, router]);

  const handleAdd = () => {
    setEditingId(null);
    setFormData({});
    setShowForm(true);
  };

  const handleEdit = (item: DataItem) => {
    setEditingId(item.id);
    setFormData(item);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
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
      }
      refreshData();
    } catch (err) {
      alert('Error deleting item');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
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
      }
      setShowForm(false);
      refreshData();
    } catch (err) {
      alert('Error saving item');
    }
  };

  const handleApproveReview = async (id: string) => {
    try {
      await reviewsAPI.approve(id);
      refreshData();
    } catch (err) {
      alert('Error approving review');
    }
  };

  const handleRejectReview = async (id: string) => {
    try {
      await reviewsAPI.reject(id);
      refreshData();
    } catch (err) {
      alert('Error rejecting review');
    }
  };

  if (!isAdmin) {
    return null;
  }

  const renderForm = () => {
    switch (activeTab) {
      case 'books':
        return (
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Title (English)"
              value={(formData.title as string) || ''}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
              required
            />
            <input
              type="text"
              placeholder="Title (Thai)"
              value={(formData.title_th as string) || ''}
              onChange={(e) => setFormData({ ...formData, title_th: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
            <textarea
              placeholder="Description (English)"
              value={(formData.description as string) || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
            <input
              type="url"
              placeholder="Cover Image URL"
              value={(formData.cover_image_url as string) || ''}
              onChange={(e) => setFormData({ ...formData, cover_image_url: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
            <select
              value={(formData.type as string) || 'manga'}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="manga">Manga</option>
              <option value="novel">Novel</option>
              <option value="light_novel">Light Novel</option>
              <option value="manhwa">Manhwa</option>
              <option value="manhua">Manhua</option>
            </select>
            <select
              value={(formData.status as string) || 'ongoing'}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="ongoing">Ongoing</option>
              <option value="completed">Completed</option>
              <option value="hiatus">Hiatus</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        );
      case 'authors':
      case 'publishers':
        return (
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Name (English)"
              value={(formData.name as string) || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
              required
            />
            <input
              type="text"
              placeholder="Name (Thai)"
              value={(formData.name_th as string) || ''}
              onChange={(e) => setFormData({ ...formData, name_th: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
            <textarea
              placeholder={activeTab === 'authors' ? 'Biography' : 'Description'}
              value={((activeTab === 'authors' ? formData.biography : formData.description) as string) || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                [activeTab === 'authors' ? 'biography' : 'description']: e.target.value 
              })}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">{t('admin.dashboard')}</h1>

        <div className="flex flex-wrap gap-2 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
              onClick={() => {
                setActiveTab(tab.key);
                setShowForm(false);
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6">
          {activeTab !== 'reviews' && (
            <button
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium mb-6 hover:bg-indigo-700 transition-colors"
              onClick={handleAdd}
            >
              + {t('admin.add')}
            </button>
          )}

          {showForm && (
            <form onSubmit={handleSubmit} className="bg-gray-50 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4">{editingId ? t('admin.edit') : t('admin.add')}</h3>
              {renderForm()}
              <div className="flex gap-3 mt-6">
                <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors">
                  {t('common.save')}
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowForm(false)}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                >
                  {t('common.cancel')}
                </button>
              </div>
            </form>
          )}

          {loading ? (
            <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>
          ) : data.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No data found</div>
          ) : activeTab === 'reviews' ? (
            <div className="space-y-4">
              {(data as Review[]).map((review) => (
                <div key={review.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="font-medium">{review.username}</span>
                      <span className="text-gray-500 mx-2">reviewed</span>
                      <span className="font-medium">{review.book_title}</span>
                    </div>
                    <span className="text-amber-400">{'⭐'.repeat(review.rating)}</span>
                  </div>
                  <p className="text-gray-700 mb-4">{review.content}</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApproveReview(review.id)}
                      className="bg-green-100 text-green-700 px-3 py-1 rounded font-medium hover:bg-green-200 transition-colors"
                    >
                      ✓ Approve
                    </button>
                    <button
                      onClick={() => handleRejectReview(review.id)}
                      className="bg-red-100 text-red-700 px-3 py-1 rounded font-medium hover:bg-red-200 transition-colors"
                    >
                      ✕ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">Name/Title</th>
                    {activeTab === 'books' && <th className="text-left py-3 px-4 font-medium text-gray-600">Type</th>}
                    {activeTab === 'books' && <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>}
                    <th className="text-right py-3 px-4 font-medium text-gray-600">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item) => (
                    <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">{'title' in item ? item.title : 'name' in item ? item.name : ''}</td>
                      {activeTab === 'books' && <td className="py-3 px-4">{(item as Book).type}</td>}
                      {activeTab === 'books' && <td className="py-3 px-4">{(item as Book).status}</td>}
                      <td className="py-3 px-4 text-right space-x-2">
                        <button
                          onClick={() => handleEdit(item)}
                          className="text-indigo-600 hover:text-indigo-800 font-medium"
                        >
                          {t('admin.edit')}
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="text-red-600 hover:text-red-800 font-medium"
                        >
                          {t('admin.delete')}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
