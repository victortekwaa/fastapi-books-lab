import logging
from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, Body, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI(title="Books API", version="1.0.0", description="A simple Books management API")

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")


@app.middleware("http")
async def log_transformed_headers(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id", "NOT present")
    apim_region = request.headers.get("x-apim-region", "NOT present")
    forwarded_for = request.headers.get("x-forwarded-for", "NOT present")

    logger.info(f"x-correlation-id: {correlation_id}")
    logger.info(f"x-apim-region: {apim_region}")
    logger.info(f"x-forwarded-for: {forwarded_for}")

    response = await call_next(request)
    return response
# --- End logging setup ---


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Books API",
        version="1.0.0",
        description="A simple Books management API",
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2029
            }
        }
    }


BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK, tags=["books"])
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK, tags=["books"])
async def read_book(book_id: int = Path(gt=0, description="The ID of the book to retrieve")):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')


@app.get("/books/", status_code=status.HTTP_200_OK, tags=["books"])
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6, description="Filter by rating (1-5)")):
    books_to_return = [book for book in BOOKS if book.rating == book_rating]
    return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK, tags=["books"])
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = [book for book in BOOKS if book.published_date == published_date]
    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED, tags=["books"])
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    return new_book


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT, tags=["books"])
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["books"])
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')