import json
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"

def read_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"articles": []}

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    headline: str
    content: str
    author: str
    category: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "draft"

@app.get("/api/articles")
def get_published_articles(category: Optional[str] = None): # Add optional category parameter
    """Get all published articles, optionally filtered by category."""
    db = read_db()
    published_articles = [
        article for article in db["articles"] if article["status"] == "published"
    ]
    
    if category: # If a category is provided, filter the results
        published_articles = [
            article for article in published_articles if article.get("category", "").lower() == category.lower()
        ]

    return sorted(published_articles, key=lambda x: x["created_at"], reverse=True)

@app.get("/api/articles/drafts")
def get_draft_articles():
    db = read_db()
    draft_articles = [
        article for article in db["articles"] if article["status"] == "draft"
    ]
    return sorted(draft_articles, key=lambda x: x["created_at"], reverse=True)

@app.post("/api/articles", status_code=201)
def create_article(article: Article):
    """Endpoint for the agent to submit a new draft article."""
    db = read_db()
    # Corrected line using .dict() for older Pydantic versions
    db["articles"].append(article.dict())
    write_db(db)
    return article

@app.patch("/api/articles/{article_id}/publish")
def publish_article(article_id: str):
    db = read_db()
    article_found = False
    for article in db["articles"]:
        if article["id"] == article_id:
            article["status"] = "published"
            article_found = True
            break
    
    if not article_found:
        raise HTTPException(status_code=404, detail="Article not found")
        
    write_db(db)
    return {"message": "Article published successfully"}

# ADD THIS NEW ENDPOINT
@app.get("/api/articles/{article_id}")
def get_article_by_id(article_id: str):
    """Get a single article by its unique ID."""
    db = read_db()
    for article in db["articles"]:
        if article["id"] == article_id:
            return article
    raise HTTPException(status_code=404, detail="Article not found")

@app.delete("/api/articles/{article_id}", status_code=200)
def delete_article(article_id: str):
    """Deletes an article by its unique ID."""
    db = read_db()
    
    # Find the article to remove
    article_to_remove = None
    for article in db["articles"]:
        if article["id"] == article_id:
            article_to_remove = article
            break
            
    if not article_to_remove:
        raise HTTPException(status_code=404, detail="Article not found")
        
    db["articles"].remove(article_to_remove)
    write_db(db)
    
    return {"message": "Article deleted successfully"}
