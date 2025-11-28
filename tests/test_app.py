import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils import add_noise_to_image, generate_captcha
from PIL import Image
import numpy as np

client = TestClient(app)

def test_home_page():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Обработка изображений с добавлением шума" in response.text

def test_captcha_generation():
    """Тест генерации CAPTCHA"""
    text, image_b64 = generate_captcha()
    assert len(text) == 6
    assert isinstance(text, str)
    assert isinstance(image_b64, str)
    assert len(image_b64) > 0

def test_noise_addition():
    """Тест добавления шума к изображению"""
    # Создание тестового изображения
    test_image = Image.new('RGB', (100, 100), color='red')
    noisy_image = add_noise_to_image(test_image, 0.1)
    
    assert test_image.size == noisy_image.size
    assert test_image.mode == noisy_image.mode
    
    # Проверка, что изображения разные (добавлен шум)
    original_pixels = np.array(test_image)
    noisy_pixels = np.array(noisy_image)
    assert not np.array_equal(original_pixels, noisy_pixels)

def test_invalid_captcha():
    """Тест обработки неверной CAPTCHA"""
    response = client.post("/process", data={
        "noise_level": "0.1",
        "captcha_input": "wrong",
        "captcha_text": "right"
    }, files={"image": ("test.jpg", b"fake image data", "image/jpeg")})
    
    assert response.status_code == 200
    assert "Неверная CAPTCHA" in response.text

if __name__ == "__main__":
    pytest.main()