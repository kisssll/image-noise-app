import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import random
import string

def add_noise_to_image(image: Image.Image, noise_level: float) -> Image.Image:
    """
    Добавляет шум к изображению
    noise_level: уровень шума от 0 до 1
    """
    # Конвертация в numpy array
    img_array = np.array(image)
    
    # Генерация шума
    noise = np.random.normal(0, noise_level * 255, img_array.shape)
    
    # Добавление шума к изображению
    noisy_array = img_array + noise
    
    # Обрезка значений до допустимого диапазона
    noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(noisy_array)

def generate_color_histograms(image: Image.Image, title: str) -> str:
    """
    Генерирует гистограмму распределения цветов
    Возвращает base64 строку с изображением гистограммы
    """
    # Конвертация в RGB если необходимо
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Получение данных пикселей
    pixels = np.array(image)
    
    # Создание гистограммы
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['red', 'green', 'blue']
    for i, color in enumerate(colors):
        ax.hist(pixels[:, :, i].ravel(), bins=256, color=color, alpha=0.7, 
                label=f'{color.title()} канал', density=True)
    
    ax.set_title(f'Распределение цветов - {title}', fontsize=14)
    ax.set_xlabel('Значение интенсивности')
    ax.set_ylabel('Плотность')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Сохранение в base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def generate_captcha() -> tuple:
    """
    Генерирует простую CAPTCHA
    Возвращает текст и изображение CAPTCHA в base64
    """
    # Генерация случайного текста
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Создание изображения
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Добавление шума к фону
    for _ in range(1000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255)
        ))
    
    # Рисование текста
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Добавление искажений к тексту
    for i, char in enumerate(text):
        x = 20 + i * 30 + random.randint(-5, 5)
        y = 20 + random.randint(-10, 10)
        draw.text((x, y), char, font=font, fill=(
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        ))
    
    # Конвертация в base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    captcha_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    return text, captcha_b64