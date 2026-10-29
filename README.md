# TOPSAN — автоматическая генерация 3D для GitHub Pages

## Что происходит
При каждом push в ветку `main` GitHub Actions устанавливает Blender на runner,
запускает `build_topsan.py`, получает `topsan_3d.glb` и публикует сайт GitHub Pages.
В браузере `index.html` загружает GLB и показывает его с интерактивным вращением.

## Установка
1. Распакуйте содержимое архива в корень GitHub-репозитория.
2. Убедитесь, что основная ветка называется `main`.
3. Откройте Settings → Pages.
4. В разделе Build and deployment выберите Source: **GitHub Actions**.
5. Загрузите файлы в репозиторий (commit/push).
6. Откройте Actions и дождитесь успешного завершения `Build TOPSAN 3D and deploy`.
7. Адрес сайта появится в Settings → Pages.

## Файлы
- `build_topsan.py` — создаёт сцену Blender и экспортирует `.blend` и `.glb`.
- `index.html` — веб-просмотрщик; загружает `topsan_3d.glb` из той же папки.
- `.github/workflows/deploy.yml` — автоматическая сборка и публикация.

Примечание: Python-скрипт выполняется в Blender на сервере GitHub Actions.
Само вращение модели выполняется в браузере через Three.js. Внешняя библиотека
Three.js загружается с CDN, поэтому при просмотре нужен интернет.
