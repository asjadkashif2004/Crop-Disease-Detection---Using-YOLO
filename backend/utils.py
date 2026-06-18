"""
utils.py
Image preprocessing and result formatting utilities.
"""

from PIL import Image
import io


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'bmp'}
MAX_IMAGE_SIZE_MB   = 10


# Nicer display names for the 30 classes
CLASS_DISPLAY_NAMES = {
    'banana_bract_mosaic_virus'    : 'Banana Bract Mosaic Virus',
    'banana_cordana'               : 'Banana Cordana Leaf Spot',
    'banana_healthy'               : 'Banana — Healthy',
    'banana_insectpest'            : 'Banana Insect Pest Damage',
    'banana_moko'                  : 'Banana Moko Disease',
    'banana_panama'                : 'Banana Panama Wilt',
    'banana_pestalotiopsis'        : 'Banana Pestalotiopsis',
    'banana_sigatoka'              : 'Banana Sigatoka',
    'banana_yb_sigatoka'           : 'Banana Yellow/Black Sigatoka',
    'cauliflower_Blackrot'         : 'Cauliflower Black Rot',
    'cauliflower_bacterial _spot _rot': 'Cauliflower Bacterial Spot Rot',
    'cauliflower_downy_mildew'     : 'Cauliflower Downy Mildew',
    'cauliflower_healthy'          : 'Cauliflower — Healthy',
    'chilli_anthracnose'           : 'Chilli Anthracnose',
    'chilli_healthy'               : 'Chilli — Healthy',
    'chilli_leafcurl'              : 'Chilli Leaf Curl',
    'chilli_leafspot'              : 'Chilli Leaf Spot',
    'chilli_whitefly'              : 'Chilli Whitefly Infestation',
    'chilli_yellowish'             : 'Chilli Yellowing',
    'groundnut_early_leaf_spot'    : 'Groundnut Early Leaf Spot',
    'groundnut_early_rust'         : 'Groundnut Early Rust',
    'groundnut_healthy'            : 'Groundnut — Healthy',
    'groundnut_late_leaf_spot'     : 'Groundnut Late Leaf Spot',
    'groundnut_nutrition_deficiency': 'Groundnut Nutrition Deficiency',
    'groundnut_rust'               : 'Groundnut Rust',
    'radish_black_leaf_spot'       : 'Radish Black Leaf Spot',
    'radish_downey_mildew'         : 'Radish Downy Mildew',
    'radish_flea_beetle'           : 'Radish Flea Beetle Damage',
    'radish_healthy'               : 'Radish — Healthy',
    'radish_mosaic'                : 'Radish Mosaic Virus',
}


DISEASE_RECOMMENDATIONS = {
    'banana_bract_mosaic_virus': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected plants and destroy affected plant material away from the field.',
            'Control aphids and other sap-sucking insects that can spread the virus.',
            'Use clean planting material and keep the field free from weeds.',
        ],
    },
    'banana_cordana': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove heavily infected leaves to reduce disease spread.',
            'Improve air circulation by keeping proper plant spacing.',
            'Use a locally approved fungicide only as directed by an agriculture expert.',
        ],
    },
    'banana_healthy': {
        'title': 'Healthy Crop Care',
        'steps': [
            'No treatment is needed for this result.',
            'Keep regular irrigation, field sanitation, and balanced fertilization.',
            'Continue monitoring leaves for early symptoms.',
        ],
    },
    'banana_insectpest': {
        'title': 'Recommended Treatment',
        'steps': [
            'Inspect the plant for visible insects, eggs, and damaged leaves.',
            'Remove badly damaged leaves and keep the field clean.',
            'Use traps or a locally recommended insect control method if pest pressure is high.',
        ],
    },
    'banana_moko': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected plants completely, including suckers and nearby plant debris.',
            'Disinfect cutting tools after use on affected plants.',
            'Avoid moving contaminated soil, water, or plant material to healthy areas.',
        ],
    },
    'banana_panama': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove severely affected plants and avoid replanting banana in infected soil.',
            'Improve drainage because wet soil can worsen wilt problems.',
            'Use resistant varieties and disease-free planting material where available.',
        ],
    },
    'banana_pestalotiopsis': {
        'title': 'Recommended Treatment',
        'steps': [
            'Prune and destroy infected leaves to lower fungal spores.',
            'Avoid overhead irrigation and reduce leaf wetness.',
            'Apply a locally approved fungicide if symptoms continue to spread.',
        ],
    },
    'banana_sigatoka': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected leaves or leaf portions when disease pressure is high.',
            'Improve field ventilation and avoid prolonged leaf wetness.',
            'Use a recommended fungicide program under local agriculture guidance.',
        ],
    },
    'banana_yb_sigatoka': {
        'title': 'Recommended Treatment',
        'steps': [
            'Cut and destroy heavily spotted leaves to reduce infection sources.',
            'Maintain good spacing, drainage, and weed control.',
            'Use locally approved fungicide sprays if the infection is spreading.',
        ],
    },
    'cauliflower_Blackrot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected plants and crop debris from the field.',
            'Avoid overhead watering and work in the field only when foliage is dry.',
            'Rotate with non-crucifer crops and use disease-free seed or seedlings.',
        ],
    },
    'cauliflower_bacterial _spot _rot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove affected leaves or plants and keep infected material out of compost.',
            'Avoid splashing water on leaves during irrigation.',
            'Use clean seed, clean tools, and crop rotation to reduce future infection.',
        ],
    },
    'cauliflower_downy_mildew': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected leaves and improve air movement around plants.',
            'Water at soil level and avoid wet leaves at night.',
            'Use a locally recommended fungicide when weather favors disease spread.',
        ],
    },
    'cauliflower_healthy': {
        'title': 'Healthy Crop Care',
        'steps': [
            'No treatment is needed for this result.',
            'Keep soil moisture consistent and avoid water stress.',
            'Monitor lower leaves regularly for spots, mildew, or rot.',
        ],
    },
    'chilli_anthracnose': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected fruits and plant debris from the field.',
            'Avoid overhead irrigation and harvest when plants are dry.',
            'Use disease-free seed and a locally approved fungicide if infection is severe.',
        ],
    },
    'chilli_healthy': {
        'title': 'Healthy Crop Care',
        'steps': [
            'No treatment is needed for this result.',
            'Maintain balanced nutrients and avoid irregular watering.',
            'Keep checking leaves and fruits for early pest or disease signs.',
        ],
    },
    'chilli_leafcurl': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove badly infected plants early to reduce virus spread.',
            'Control whiteflies using yellow sticky traps or locally recommended methods.',
            'Use healthy seedlings and keep weeds controlled around the crop.',
        ],
    },
    'chilli_leafspot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected leaves and crop debris.',
            'Avoid wetting foliage and increase spacing for better air flow.',
            'Apply a locally approved fungicide or bactericide based on expert advice.',
        ],
    },
    'chilli_whitefly': {
        'title': 'Recommended Treatment',
        'steps': [
            'Use yellow sticky traps to monitor and reduce adult whiteflies.',
            'Remove weeds and heavily infested leaves from the growing area.',
            'Use a locally recommended insect control method if the infestation is heavy.',
        ],
    },
    'chilli_yellowish': {
        'title': 'Recommended Treatment',
        'steps': [
            'Check soil moisture, drainage, and nutrient balance first.',
            'Inspect leaf undersides for whiteflies, mites, or other sucking pests.',
            'Apply balanced fertilizer or pest control only after confirming the cause.',
        ],
    },
    'groundnut_early_leaf_spot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected crop residues after harvest.',
            'Avoid dense planting and keep the field well ventilated.',
            'Use a locally approved fungicide if spotting spreads quickly.',
        ],
    },
    'groundnut_early_rust': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove volunteer plants and infected debris that can carry spores.',
            'Avoid overhead irrigation and reduce humidity around the crop.',
            'Use resistant varieties or a locally recommended fungicide where available.',
        ],
    },
    'groundnut_healthy': {
        'title': 'Healthy Crop Care',
        'steps': [
            'No treatment is needed for this result.',
            'Maintain proper field drainage and balanced nutrition.',
            'Monitor leaves regularly during humid weather.',
        ],
    },
    'groundnut_late_leaf_spot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected crop debris and rotate with non-host crops.',
            'Improve field airflow and avoid prolonged leaf wetness.',
            'Use a locally approved fungicide when disease pressure is high.',
        ],
    },
    'groundnut_nutrition_deficiency': {
        'title': 'Recommended Treatment',
        'steps': [
            'Check soil pH and nutrient status with a soil test if possible.',
            'Apply balanced fertilizer based on the crop stage and local recommendations.',
            'Keep irrigation consistent so roots can absorb nutrients properly.',
        ],
    },
    'groundnut_rust': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected residues and avoid planting groundnut repeatedly in the same field.',
            'Reduce leaf wetness by improving spacing and irrigation practice.',
            'Use resistant varieties or a locally recommended fungicide if rust spreads.',
        ],
    },
    'radish_black_leaf_spot': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected leaves and crop debris from the field.',
            'Avoid overhead watering and improve spacing for air movement.',
            'Rotate with non-crucifer crops and use clean seed.',
        ],
    },
    'radish_downey_mildew': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected leaves and avoid working with wet plants.',
            'Water at soil level and keep good spacing between plants.',
            'Use a locally approved fungicide if cool, humid weather continues.',
        ],
    },
    'radish_flea_beetle': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove weeds and crop debris where beetles can hide.',
            'Use row covers or sticky traps for early protection where practical.',
            'Use a locally recommended insect control method if damage is severe.',
        ],
    },
    'radish_healthy': {
        'title': 'Healthy Crop Care',
        'steps': [
            'No treatment is needed for this result.',
            'Keep soil evenly moist for steady root growth.',
            'Monitor leaves for spots, holes, or mildew during crop growth.',
        ],
    },
    'radish_mosaic': {
        'title': 'Recommended Treatment',
        'steps': [
            'Remove infected plants because viral diseases cannot be cured in the plant.',
            'Control aphids and weeds that may spread the virus.',
            'Use healthy seed and rotate crops to reduce future risk.',
        ],
    },
}


def get_recommendation(class_name):
    """
    Returns crop care or treatment guidance for the predicted class.
    """
    if class_name == 'no_detection':
        return {
            'title': 'No Disease Detected',
            'steps': [
                'No treatment is needed for this result.',
                'Upload a clearer leaf image if symptoms are visible but were not detected.',
                'Continue monitoring the crop regularly.',
            ],
        }

    return DISEASE_RECOMMENDATIONS.get(class_name, {
        'title': 'General Recommendation',
        'steps': [
            'Remove visibly infected leaves or plant parts if symptoms are spreading.',
            'Improve field hygiene, spacing, drainage, and irrigation practice.',
            'Consult a local agriculture expert before using chemical treatment.',
        ],
    })


def validate_image(file):
    """
    Validates the uploaded file.
    Returns (True, None) if valid, (False, error_message) if not.
    """
    # Check extension
    filename  = file.name.lower()
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '.{extension}'. Please upload JPG, PNG, or WEBP."

    # Check file size
    if file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Maximum allowed size is {MAX_IMAGE_SIZE_MB}MB."

    # Try opening as image
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        return False, "File is not a valid image."

    # Reset file pointer after verify
    file.seek(0)
    return True, None


def preprocess_image(file):
    """
    Opens and returns a PIL Image ready for YOLO inference.
    YOLO handles its own resizing internally, so we just open it.
    """
    file.seek(0)
    image = Image.open(file).convert('RGB')
    return image


def format_prediction(results, model):
    """
    Extracts the top prediction from YOLO results.
    Returns dict with class name, display name, and confidence.
    """
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return {
            'class_name'   : 'no_detection',
            'display_name' : 'No Disease Detected',
            'confidence'   : 0.0,
            'detected'     : False,
        }

    # Get the box with highest confidence
    confidences = boxes.conf.cpu().numpy()
    class_ids   = boxes.cls.cpu().numpy().astype(int)

    best_idx    = confidences.argmax()
    best_conf   = float(confidences[best_idx])
    best_class  = int(class_ids[best_idx])

    # Get class name from model
    class_name  = model.names[best_class]
    display_name = CLASS_DISPLAY_NAMES.get(class_name, class_name.replace('_', ' ').title())

    return {
        'class_name'  : class_name,
        'display_name': display_name,
        'confidence'  : round(best_conf, 4),
        'detected'    : True,
    }
