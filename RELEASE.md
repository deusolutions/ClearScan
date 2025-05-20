# Release Checklist: ClearScan

## Перед релизом
- [x] Все тесты проходят (`pytest`, `flake8`)
- [x] Документация актуальна (README.md, CONTRIBUTING.md, docs/)
- [x] requirements.txt содержит все зависимости
- [x] CI/CD (GitHub Actions) работает корректно
- [x] Версия и CHANGELOG.md обновлены
- [x] Нет секретов/токенов в коде

## Выпуск релиза
1. Обновите CHANGELOG.md и README.md
2. Создайте git-тег:
   ```powershell
   git tag v1.0.0
   git push --tags
   ```
3. Оформите релиз на GitHub Releases (описание, ссылки, changelog)
4. Проверьте, что CI/CD прошёл успешно
5. Сообщите команде и пользователям о релизе

---

(c) 2023-2025 Deus Solutions
