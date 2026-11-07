from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Phone, Report, Base, engine
from datetime import datetime
import os

app = FastAPI(title="Lost Phone Tracker")
templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    phones = db.query(Phone).order_by(Phone.created_at.desc()).limit(20).all()
    return templates.TemplateResponse("index.html", {"request": request, "phones": phones})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_phone(
    imei: str = Form(...),
    serial_number: str = Form(""),
    brand: str = Form(""),
    model: str = Form(""),
    color: str = Form(""),
    storage: str = Form(""),
    purchase_date: str = Form(""),
    store_name: str = Form(""),
    store_location: str = Form(""),
    price: str = Form(""),
    receipt_number: str = Form(""),
    warranty_expiry: str = Form(""),
    owner_name: str = Form(""),
    owner_phone: str = Form(""),
    owner_email: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    if len(imei) != 15 or not imei.isdigit():
        raise HTTPException(status_code=400, detail="IMEI must be 15 digits")
    existing = db.query(Phone).filter(Phone.imei == imei).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    phone = Phone(
        imei=imei, serial_number=serial_number, brand=brand, model=model,
        color=color, storage=storage, purchase_date=purchase_date, store_name=store_name,
        store_location=store_location, price=price, receipt_number=receipt_number,
        warranty_expiry=warranty_expiry, owner_name=owner_name, owner_phone=owner_phone,
        owner_email=owner_email, notes=notes, status="registered"
    )
    db.add(phone)
    db.commit()
    return RedirectResponse(url=f"/phone/{phone.id}", status_code=303)

@app.get("/phone/{phone_id}", response_class=HTMLResponse)
def phone_detail(request: Request, phone_id: int, db: Session = Depends(get_db)):
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Not found")
    reports = db.query(Report).filter(Report.phone_id == phone_id).order_by(Report.created_at.desc()).all()
    return templates.TemplateResponse("detail.html", {"request": request, "phone": phone, "reports": reports})

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.post("/search", response_class=HTMLResponse)
def search_phone(request: Request, query: str = Form(...), db: Session = Depends(get_db)):
    q = query.strip()
    phone = db.query(Phone).filter((Phone.imei == q) | (Phone.serial_number == q) | (Phone.receipt_number == q)).first()
    if not phone:
        return templates.TemplateResponse("search.html", {"request": request, "query": q, "not_found": True})
    return RedirectResponse(url=f"/phone/{phone.id}", status_code=303)

@app.post("/report/{phone_id}")
def add_report(
    phone_id: int,
    report_type: str = Form(...),
    reporter_name: str = Form(""),
    reporter_phone: str = Form(""),
    reporter_email: str = Form(""),
    location: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Not found")
    report = Report(phone_id=phone_id, imei=phone.imei, report_type=report_type,
                    reporter_name=reporter_name, reporter_phone=reporter_phone,
                    reporter_email=reporter_email, location=location, description=description)
    db.add(report)
    if report_type == "lost":
        phone.status = "lost"
    elif report_type == "found":
        phone.status = "found"
    phone.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(url=f"/phone/{phone_id}", status_code=303)

@app.get("/status/{status}", response_class=HTMLResponse)
def by_status(request: Request, status: str, db: Session = Depends(get_db)):
    phones = db.query(Phone).filter(Phone.status == status).order_by(Phone.created_at.desc()).all()
    return templates.TemplateResponse("list.html", {"request": request, "phones": phones, "title": status.capitalize() + " Phones"})

@app.get("/api/phones")
def api_phones(db: Session = Depends(get_db)):
    return db.query(Phone).all()

@app.get("/api/phone/{imei}")
def api_phone(imei: str, db: Session = Depends(get_db)):
    phone = db.query(Phone).filter(Phone.imei == imei).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Not found")
    return phone
