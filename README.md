# 1. Клонируем репозиторий
git clone https://github.com/vadailin/RuslanShevchencko 

# 2. Переходим в папку проекта
cd RuslanShevchencko

# 3. Создаем виртуальное окружение (в Windows вместо python3 используется python)
python -m venv venv

# 4. Активируем виртуальное окружение (путь к скрипту в Windows отличается)
.\venv\Scripts\activate

# 5. Устанавливаем зависимости (исправлена опечатка в слове requirements)
pip install -r requirements.txt
