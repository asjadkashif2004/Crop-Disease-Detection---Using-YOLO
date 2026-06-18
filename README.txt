# Edge AI Crop Disease Detection — Django Web App
# ================================================
# BUITEMS FYP 2025 | Syed Muhammad Ibraheem Athar

## STEP 1 — Install dependencies
# Open Command Prompt and run:

pip install django djangorestframework django-cors-headers Pillow

## STEP 2 — Set your model path
# Open: crop_disease_project/settings.py
# Find line at the bottom:
#   MODEL_WEIGHTS_PATH = r"E:\BUITEMS\..."
# Change it to your actual best.pt path, e.g.:
#   MODEL_WEIGHTS_PATH = r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset\runs\detect\fyp_crop_disease\run1\weights\best.pt"

## STEP 3 — Run the server
# Open Command Prompt, navigate to this folder, then run:

python manage.py runserver

## STEP 4 — Open the website
# Open your browser and go to:
#   http://localhost:8000
#   http://127.0.0.1:8000

## FOLDER STRUCTURE
# crop_disease_app/
# ├── manage.py
# ├── requirements.txt
# ├── crop_disease_project/
# │   ├── settings.py       ← SET YOUR MODEL PATH HERE
# │   └── urls.py
# ├── backend/
# │   ├── views.py          ← API logic
# │   ├── model_loader.py   ← loads YOLO model
# │   └── utils.py          ← preprocessing & formatting
# └── frontend/
#     ├── templates/
#     │   └── index.html    ← single page UI
#     └── static/
#         ├── css/style.css ← neon dark theme
#         └── js/app.js     ← AJAX logic
