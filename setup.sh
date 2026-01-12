#!/bin/bash

echo "🚀 Налаштування CI/CD проєкту..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не знайдено. Встановіть Python 3.9 або новішу версію."
    exit 1
fi

echo "✅ Python версія: $(python3 --version)"
echo ""

echo "📦 Створення віртуального середовища..."
python3 -m venv venv

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Віртуальне середовище створено"
echo ""

echo "📥 Встановлення залежностей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Залежності встановлено"
echo ""

echo "🧪 Запуск тестів..."
pytest test_app.py -v

echo ""
echo "📊 Генерація звіту покриття..."
pytest test_app.py --cov=app --cov-report=html --cov-report=term

echo ""
echo "🔍 Лінтинг коду..."
flake8 app.py --max-line-length=120 --statistics || true
pylint app.py --disable=C0103,C0114,C0115,C0116 || true

echo ""
echo "✨ Перевірка форматування..."
black --check app.py test_app.py || true

echo ""
echo "✅ Налаштування завершено!"
echo ""
echo "🌐 Для запуску додатку виконайте:"
echo "   source venv/bin/activate  # Linux/Mac"
echo "   venv\\Scripts\\activate    # Windows"
echo "   python app.py"
echo ""
echo "🐳 Або запустіть через Docker:"
echo "   docker-compose up -d"
echo ""
echo "📊 Звіт покриття коду доступний в htmlcov/index.html"
