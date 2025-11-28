from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from .utils import add_noise_to_image, generate_color_histograms, generate_captcha

app = FastAPI(title="Image Noise App")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с формой загрузки изображения"""
    captcha_text, captcha_image = generate_captcha()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "captcha_text": captcha_text,
        "captcha_image": captcha_image
    })

@app.post("/process", response_class=HTMLResponse)
async def process_image(
    request: Request,
    image: UploadFile = File(...),
    noise_level: float = Form(...),
    captcha_input: str = Form(...),
    captcha_text: str = Form(...)
):
    """Обработка изображения и добавление шума"""
    
    # Проверка CAPTCHA
    if captcha_input != captcha_text:
        new_captcha_text, new_captcha_image = generate_captcha()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Неверная CAPTCHA",
            "captcha_text": new_captcha_text,
            "captcha_image": new_captcha_image
        })
    
    try:
        # Чтение и обработка изображения
        image_data = await image.read()
        original_image = Image.open(BytesIO(image_data))
        
        # Добавление шума
        noisy_image = add_noise_to_image(original_image, noise_level)
        
        # Генерация гистограмм
        original_histogram = generate_color_histograms(original_image, "Исходное изображение")
        noisy_histogram = generate_color_histograms(noisy_image, "Зашумленное изображение")
        
        # Конвертация изображений в base64 для отображения в HTML
        buffered_original = BytesIO()
        original_image.save(buffered_original, format="PNG")
        original_b64 = base64.b64encode(buffered_original.getvalue()).decode()
        
        buffered_noisy = BytesIO()
        noisy_image.save(buffered_noisy, format="PNG")
        noisy_b64 = base64.b64encode(buffered_noisy.getvalue()).decode()
        
        # Генерация новой CAPTCHA
        new_captcha_text, new_captcha_image = generate_captcha()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "original_image": original_b64,
            "noisy_image": noisy_b64,
            "original_histogram": original_histogram,
            "noisy_histogram": noisy_histogram,
            "captcha_text": new_captcha_text,
            "captcha_image": new_captcha_image,
            "success": "Изображение успешно обработано!"
        })
        
    except Exception as e:
        new_captcha_text, new_captcha_image = generate_captcha()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Ошибка обработки изображения: {str(e)}",
            "captcha_text": new_captcha_text,
            "captcha_image": new_captcha_image
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)