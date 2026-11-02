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