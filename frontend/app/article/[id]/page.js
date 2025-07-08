import Link from 'next/link';

async function getArticle(articleId) {
  const res = await fetch(`http://127.0.0.1:8000/api/articles/${articleId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch the article');
  }
  return res.json();
}

// A dedicated component for styling blockquotes
function Blockquote({ children }) {
  return (
    <blockquote className="my-6 p-4 border-l-4 border-brand-red bg-red-50 text-xl italic text-gray-700">
      {children}
    </blockquote>
  );
}

// Our new smart parser function
function parseArticleContent(content) {
  const blocks = content.split('\n\n');

  return blocks.map((block, index) => {
    // Rule for markdown headings: if a block starts and ends with **
    if (block.startsWith('**') && block.endsWith('**')) {
      // Remove the wrapping asterisks and render as an h2 heading
      return <h2 key={index} className="font-serif text-2xl md:text-3xl font-bold text-gray-900 my-6">{block.slice(2, -2)}</h2>;
    }
    
    // Rule for quotes: if a block starts and ends with a quote
    if (block.startsWith('"') && block.endsWith('"')) {
      return <Blockquote key={index}>{block.slice(1, -1)}</Blockquote>;
    }
    
    // Default to a regular paragraph
    return <p key={index} className="my-4">{block}</p>;
  });
}


export default async function ArticlePage({ params }) {
  const article = await getArticle(params.id);
  
  // Use the new parser to generate the article body components
  const articleBody = parseArticleContent(article.content);

  return (
    <div>
      <div className="mb-8">
        <Link href="/" className="text-brand-red hover:underline">
          &larr; Back to All Stories
        </Link>
      </div>

      <article className="max-w-4xl mx-auto bg-white p-6 sm:p-8 md:p-10 rounded-lg shadow-lg border">
        
        <div className="mb-6">
          <img 
            src={`https://picsum.photos/seed/${article.id}/1200/600`} 
            alt={article.headline}
            className="w-full h-auto rounded-lg object-cover"
          />
          <p className="text-xs text-gray-400 text-center mt-2">A representational image for the story.</p>
        </div>

        <h1 className="font-serif text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          {article.headline}
        </h1>
        
        <div className="text-sm text-gray-500 mb-8 border-y py-4 flex justify-between items-center">
          <span>By {article.author}</span>
          <span>Published on {new Date(article.created_at).toLocaleDateString()}</span>
        </div>

        {/* The output of our parser is rendered here */}
        <div className="prose prose-lg max-w-none prose-p:text-gray-800">
          {articleBody}
        </div>
      </article>
    </div>
  );
}