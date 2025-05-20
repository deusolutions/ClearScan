# Contributing to ClearScan

Thank you for considering contributing to this project!

## CI/CD
- Все коммиты и pull requests автоматически проверяются через GitHub Actions.
- Проверки включают:
  - Линтинг кода с помощью flake8 (директория `src/`).
  - Запуск тестов с помощью pytest.
- Файл workflow: `.github/workflows/ci.yml`.
- Перед отправкой изменений убедитесь, что ваш код проходит flake8 и pytest локально:

```bash
pip install -r requirements.txt
pip install flake8 pytest
flake8 src
pytest
```

## Pull Requests
- Описывайте изменения в PR.
- Следите за чистотой истории коммитов.
- Не забывайте обновлять документацию при необходимости.

Спасибо за ваш вклад!
