'use client';
import { useState, useEffect } from 'react';
// You can remove the import for 'styles' if it's still there.

export default function AdminPage() {
  const [drafts, setDrafts] = useState([]);
  const [message, setMessage] = useState('');

  const fetchDrafts = async () => {
    const res = await fetch('http://127.0.0.1:8000/api/articles/drafts');
    const data = await res.json();
    setDrafts(data);
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

  const handlePublish = async (articleId) => {
    setMessage('Publishing...');
    await fetch(`http://127.0.0.1:8000/api/articles/${articleId}/publish`, {
      method: 'PATCH',
    });
    setMessage('Article published successfully! Refreshing drafts...');
    // Refresh the list of drafts after publishing
    fetchDrafts();
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    // Replaced styles.main with Tailwind utility classes
    <main className="flex min-h-screen flex-col items-center p-8 sm:p-12 md:p-24 bg-gray-100">
      <header className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-800">Admin Panel</h1>
        <p className="text-lg text-gray-600 mt-2">Approve Drafts to Publish</p>
        
        {/* Styled message for user feedback */}
        {message && (
          <p className="mt-4 p-3 bg-green-100 text-green-800 rounded-lg shadow-sm">
            {message}
          </p>
        )}
      </header>
      
      {/* Replaced styles.grid with Tailwind utility classes */}
      <div className="grid grid-cols-1 gap-8 w-full max-w-4xl">
        {drafts.length > 0 ? (
          drafts.map((draft) => (
            // Replaced styles.card with Tailwind utility classes for a card-like look
            <div key={draft.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-md">
              <h2 className="text-2xl font-bold text-gray-900 mb-3">{draft.headline}</h2>
              {/* Using prose to nicely format the article content */}
              <article className="prose lg:prose-xl text-gray-700 mb-6">
                <p>{draft.content}</p>
              </article>
              
              {/* Replaced styles.button with Tailwind utility classes */}
              <button 
                onClick={() => handlePublish(draft.id)} 
                className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 transition-colors"
              >
                Publish
              </button>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500">
            No drafts waiting for approval. Run the agent to create one!
          </p>
        )}
      </div>
    </main>
  );
}