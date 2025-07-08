import Link from 'next/link';

/**
 * Fetches articles from the API, optionally filtering by category.
 * @param {string | null} category - The category to filter articles by.
 * @returns {Promise<Array>} A promise that resolves to an array of articles.
 */
async function getArticles(category) {
  // Base URL for the articles API
  let url = 'http://127.0.0.1:8000/api/articles';

  // If a category is provided, append it as a query parameter
  if (category) {
    url += `?category=${encodeURIComponent(category)}`;
  }

  // Fetch data with caching disabled to ensure freshness
  const res = await fetch(url, { cache: 'no-store' });

  // Handle potential errors during the fetch
  if (!res.ok) {
    throw new Error('Failed to fetch articles');
  }

  return res.json();
}

/**
 * A reusable UI component to display a single article card.
 * @param {object} props - The component props.
 * @param {object} props.article - The article object to display.
 * @returns {JSX.Element}
 */
function ArticleCard({ article }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border flex flex-col hover:shadow-lg transition-shadow">
      <h3 className="font-serif text-xl font-bold text-gray-900 mb-2">
        <Link href={`/article/${article.id}`} className="hover:text-brand-red">
          {article.headline}
        </Link>
      </h3>
      <p className="text-gray-600 text-sm mb-3 flex-grow">{article.content.substring(0, 120)}...</p>
      <small className="text-gray-500">{new Date(article.created_at).toLocaleDateString()}</small>
    </div>
  );
}

/**
 * The main homepage component that displays articles.
 * It can filter articles based on the 'category' URL search parameter.
 * @param {object} props - The component props.
 * @param {object} props.searchParams - The URL search parameters.
 * @returns {JSX.Element}
 */
export default async function Home({ searchParams }) {
  // Get the category from URL query, or null if it doesn't exist
  const category = searchParams.category || null;
  const articles = await getArticles(category);

  // Separate the first article as the "hero" story
  const heroArticle = articles[0];
  const otherArticles = articles.slice(1);

  // Dynamically set the page title based on whether a category is active
  const pageTitle = category ? `${category} News` : "Top Stories";

  return (
    <div>
      <h1 className="font-serif text-2xl font-bold text-gray-800 border-b-2 border-brand-red pb-2 mb-6">
        {pageTitle}
      </h1>

      {articles.length > 0 ? (
        <>
          {/* Hero Article Section */}
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h2 className="font-serif text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              <Link href={`/article/${heroArticle.id}`} className="hover:text-brand-red">
                {heroArticle.headline}
              </Link>
            </h2>
            <p className="text-gray-700 mb-4">{heroArticle.content.substring(0, 250)}...</p>
            <small className="text-gray-500">By {heroArticle.author} on {new Date(heroArticle.created_at).toLocaleDateString()}</small>
          </div>

          {/* Grid for Other Articles */}
          <h2 className="font-serif text-2xl font-bold text-gray-800 border-b-2 border-brand-red pb-2 mb-6">More Stories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {otherArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </>
      ) : (
        <p className="text-center text-gray-500 py-16">
          No articles found for this category.
        </p>
      )}
    </div>
  );
}