'use client';
import { useState, useEffect } from 'react';

// A reusable confirmation modal component (no changes needed here)
function ConfirmationModal({ message, onConfirm, onCancel }) {
  // ... (code from previous step remains the same)
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg shadow-2xl text-center max-w-sm mx-4">
        <p className="text-lg font-semibold mb-6">{message}</p>
        <div className="flex justify-center space-x-4">
          <button 
            onClick={onCancel}
            className="px-6 py-2 bg-gray-300 text-gray-800 font-semibold rounded-lg hover:bg-gray-400 transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm}
            className="px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
          >
            Confirm Delete
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminPage() {
  const [drafts, setDrafts] = useState([]);
  const [published, setPublished] = useState([]);
  const [message, setMessage] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [articleToDelete, setArticleToDelete] = useState(null);
  
  // New state for UI control
  const [activeTab, setActiveTab] = useState('drafts'); // 'drafts' or 'published'
  const [expandedDraftId, setExpandedDraftId] = useState(null); // To track which draft is open

  const fetchData = async () => {
    // Fetching logic remains the same
    const draftsRes = await fetch('http://127.0.0.1:8000/api/articles/drafts');
    const draftsData = await draftsRes.json();
    setDrafts(draftsData);

    const publishedRes = await fetch('http://127.0.0.1:8000/api/articles');
    const publishedData = await publishedRes.json();
    setPublished(publishedData);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePublish = async (articleId) => {
    // ... (logic remains the same)
    setMessage('Publishing...');
    await fetch(`http://127.0.0.1:8000/api/articles/${articleId}/publish`, { method: 'PATCH' });
    setMessage('Article published successfully!');
    fetchData();
    setTimeout(() => setMessage(''), 3000);
  };

  const handleDeleteClick = (articleId) => {
    // ... (logic remains the same)
    setArticleToDelete(articleId);
    setShowModal(true);
  };

  const confirmDelete = async () => {
    // ... (logic remains the same)
    if (!articleToDelete) return;
    setMessage('Deleting...');
    await fetch(`http://127.0.0.1:8000/api/articles/${articleToDelete}`, { method: 'DELETE' });
    setMessage('Article deleted successfully!');
    setShowModal(false);
    setArticleToDelete(null);
    fetchData();
    setTimeout(() => setMessage(''), 3000);
  };

  const toggleDraft = (draftId) => {
    if (expandedDraftId === draftId) {
      setExpandedDraftId(null); // Collapse if already open
    } else {
      setExpandedDraftId(draftId); // Expand the clicked draft
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 sm:p-12 md:p-24 bg-gray-100">
      {showModal && (
        <ConfirmationModal 
          message="Are you sure you want to permanently delete this article?"
          onConfirm={confirmDelete}
          onCancel={() => setShowModal(false)}
        />
      )}
      <header className="text-center mb-12 w-full max-w-5xl">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-800">Admin Panel</h1>
        <p className="text-lg text-gray-600 mt-2">Manage all articles</p>
        {message && <p className="mt-4 p-3 bg-green-100 text-green-800 rounded-lg">{message}</p>}
      </header>
      
      <div className="w-full max-w-5xl">
        {/* Tab Navigation */}
        <div className="border-b border-gray-300 mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('drafts')}
              className={`py-4 px-1 border-b-2 font-medium text-lg ${activeTab === 'drafts' ? 'border-brand-red text-brand-red' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-400'}`}
            >
              Drafts ({drafts.length})
            </button>
            <button
              onClick={() => setActiveTab('published')}
              className={`py-4 px-1 border-b-2 font-medium text-lg ${activeTab === 'published' ? 'border-brand-red text-brand-red' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-400'}`}
            >
              Published ({published.length})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'drafts' && (
            <div className="space-y-6">
              {drafts.length > 0 ? drafts.map((draft) => (
                <div key={draft.id} className="bg-white rounded-lg shadow-md border">
                  {/* Clickable Header for Toggling */}
                  <div className="p-6 cursor-pointer hover:bg-gray-50" onClick={() => toggleDraft(draft.id)}>
                    <div className="flex justify-between items-center">
                      <h3 className="text-2xl font-bold text-gray-900">{draft.headline}</h3>
                      <span className={`transform transition-transform duration-300 ${expandedDraftId === draft.id ? 'rotate-180' : ''}`}>▼</span>
                    </div>
                  </div>
                  
                  {/* Expandable Content Area */}
                  {expandedDraftId === draft.id && (
                    <div className="p-6 border-t border-gray-200">
                      <article className="prose lg:prose-xl text-gray-700 mb-6">
                        <p>{draft.content}</p>
                      </article>
                      <div className="flex space-x-4">
                        <button onClick={(e) => { e.stopPropagation(); handlePublish(draft.id); }} className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">Publish</button>
                        <button onClick={(e) => { e.stopPropagation(); handleDeleteClick(draft.id); }} className="px-6 py-2 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors">Delete Draft</button>
                      </div>
                    </div>
                  )}
                </div>
              )) : <p className="text-gray-500 text-center py-8">No drafts are waiting for approval.</p>}
            </div>
          )}

          {activeTab === 'published' && (
             <div className="space-y-4">
              {published.length > 0 ? published.map((article) => (
                <div key={article.id} className="bg-white p-4 rounded-lg shadow-md flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{article.headline}</h3>
                    <p className="text-sm text-gray-500 mt-1">Published on: {new Date(article.created_at).toLocaleDateString()}</p>
                  </div>
                  <button onClick={() => handleDeleteClick(article.id)} className="px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors">Delete</button>
                </div>
              )) : <p className="text-gray-500 text-center py-8">No articles have been published yet.</p>}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}