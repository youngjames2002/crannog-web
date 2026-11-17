from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="pages")

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

ITEMS = [
    {
        'id': 1, 'name': 'Item 1', 'price': 19.99,
        'short-description': 'This is an example item description.',
        'long-description': 'A longer description of the item, covering the design, the story behind it and how it wears.',
        'images': ['https://via.placeholder.com/300', 'https://via.placeholder.com/300'],
        'colour': 'Black', 'sizes': ['S', 'M', 'L', 'XL'], 'material': '100% cotton',
        'fit': 'Regular fit', 'care': 'Machine wash cold, do not tumble dry', 'stock': 12, 'artist': 'artist-1',
    },
    {
        'id': 2, 'name': 'Item 2', 'price': 29.99,
        'short-description': 'This is an example item description.',
        'long-description': 'A longer description of the item, covering the design, the story behind it and how it wears.',
        'images': ['https://via.placeholder.com/300'],
        'colour': 'Green', 'sizes': ['M', 'L'], 'material': '80% cotton, 20% polyester',
        'fit': 'Oversized fit', 'care': 'Machine wash 30°C', 'stock': 3, 'artist': 'artist-2',
    },
    {
        'id': 3, 'name': 'Item 3', 'price': 39.99,
        'short-description': 'This is an example item description.',
        'long-description': 'A longer description of the item, covering the design, the story behind it and how it wears.',
        'images': ['https://via.placeholder.com/300'],
        'colour': 'Navy', 'sizes': ['S', 'M', 'L'], 'material': '100% wool',
        'fit': 'Regular fit', 'care': 'Hand wash only', 'stock': 0, 'artist': 'artist-3',
    },
]

ARTISTS = [
    {
        'slug': 'artist-1', 'name': 'Artist 1',
        'bio': 'A short bio about the artist, their background and the work they make.',
        'portrait': 'https://via.placeholder.com/200',
        'images': ['https://via.placeholder.com/300', 'https://via.placeholder.com/300', 'https://via.placeholder.com/300'],
        'links': [
            {'label': 'Instagram', 'url': 'https://example.com/artist-1-instagram'},
            {'label': 'Website', 'url': 'https://example.com/artist-1'},
        ],
    },
    {
        'slug': 'artist-2', 'name': 'Artist 2',
        'bio': 'A short bio about the artist, their background and the work they make.',
        'portrait': 'https://via.placeholder.com/200',
        'images': ['https://via.placeholder.com/300', 'https://via.placeholder.com/300'],
        'links': [
            {'label': 'Instagram', 'url': 'https://example.com/artist-2-instagram'},
        ],
    },
    {
        'slug': 'artist-3', 'name': 'Artist 3',
        'bio': 'A short bio about the artist, their background and the work they make.',
        'portrait': 'https://via.placeholder.com/200',
        'images': ['https://via.placeholder.com/300'],
        'links': [
            {'label': 'Website', 'url': 'https://example.com/artist-3'},
        ],
    },
]

def find_artist(slug):
    return next((a for a in ARTISTS if a['slug'] == slug), None)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/explore")
def explore(request: Request):
    artists = {a['slug']: a for a in ARTISTS}
    return templates.TemplateResponse(request, "explore.html", {"items": ITEMS, "artists": artists})

@app.get("/explore/{item_id}")
def item_detail(request: Request, item_id: int):
    item = next((i for i in ITEMS if i['id'] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    artist = find_artist(item['artist'])
    return templates.TemplateResponse(request, "item.html", {"item": item, "artist": artist})

@app.get("/who-we-are")
def artists(request: Request):
    return templates.TemplateResponse(request, "who-we-are.html", {"artists": ARTISTS})

@app.get("/artist/{artist_slug}")
def artist_detail(request: Request, artist_slug: str):
    artist = find_artist(artist_slug)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    items = [i for i in ITEMS if i['artist'] == artist_slug]
    return templates.TemplateResponse(request, "artist.html", {"artist": artist, "items": items})

@app.get("/who-we-are")
def who_we_are(request: Request):
    return templates.TemplateResponse(request, "who-we-are.html")

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")

@app.get("/checkout")
def checkout(request: Request):
    return templates.TemplateResponse(request, "checkout.html")

@app.post("/payment")
def payment(request: Request):
    print("Payment processing logic goes here")

@app.get("/payment-success")
def payment_success(request: Request):
    return templates.TemplateResponse(request, "payment-success.html")

@app.get("/payment-cancelled")
def payment_cancelled(request: Request): 
    return templates.TemplateResponse(request, "payment-cancelled.html")

@app.get("/add-to-basket/{item_id}")
def add_to_basket(request: Request, item_id: int):
    # Logic to add the item to the basket goes here
    print(f"Item {item_id} added to basket")
    return templates.TemplateResponse(request, "basket.html", {"item_id": item_id})