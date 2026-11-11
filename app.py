from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="pages")

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/explore")
def explore(request: Request):
    return templates.TemplateResponse(request, "explore.html")

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