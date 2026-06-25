"""Flask application for Brain Tumor MRI classification with Grad-CAM explainability."""

import os
import sys
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
from typing import Tuple
import io
import numpy as np

import torch

# Ensure src modules are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from predict import load_model, preprocess_image, predict_image
from explain import explain
from database import save_prediction, get_all_predictions, get_statistics, delete_prediction
from tumor_info import get_tumor_info, get_general_tumor_info, get_tumor_type_suggestions
from doctors_directory import get_recommended_doctors, get_all_doctors, get_doctors_by_expertise
from enhanced_explainability import generate_detailed_explanation, explain_model_decision

import time  


UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
RESULTS_FOLDER = PROJECT_ROOT / "results"
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pth"

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = load_model(str(MODEL_PATH), device=DEVICE)


app = Flask(__name__, template_folder="templates", static_folder="static")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MIN_IMAGE_SIZE = 50  # Minimum width/height in pixels


def allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_medical_image(image: PILImage.Image) -> Tuple[bool, str]:
    """
    Check if the image appears to be a medical image (MRI or X-ray).
    Medical images typically have:
    - Grayscale or low color saturation
    - Specific contrast patterns
    - Medical scan characteristics
    """
    try:
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Check 1: Grayscale check - medical images are typically grayscale
        # Calculate color saturation (how much color vs grayscale)
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        
        # Calculate standard deviation of RGB channels
        # In grayscale images, R, G, B should be similar
        std_r = np.std(r)
        std_g = np.std(g)
        std_b = np.std(b)
        
        # Calculate average difference between channels
        mean_diff = np.mean(np.abs(r.astype(float) - g.astype(float)) + 
                           np.abs(g.astype(float) - b.astype(float)) + 
                           np.abs(r.astype(float) - b.astype(float))) / 3
        
        # Medical images typically have low color variation (mostly grayscale)
        # Threshold: if mean difference is too high, it's likely a color photo
        # Made stricter for brain MRI (should be very grayscale)
        if mean_diff > 25:  # Stricter threshold for brain MRI (should be very grayscale)
            return False, "This appears to be a color photograph, not a brain MRI scan. Brain MRI images are grayscale. Please upload a brain MRI image."
        
        # Check 2: Contrast check - medical images usually have good contrast
        # Convert to grayscale for contrast analysis
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        contrast = np.std(gray)
        
        # Very low contrast might indicate it's not a medical scan
        # Brain MRIs typically have good contrast
        if contrast < 20:  # Stricter contrast requirement for brain MRI
            return False, "Image has very low contrast. Brain MRI scans typically have higher contrast. Please upload a clear brain MRI image."
        
        # Check 3: Brightness distribution - medical images often have specific histogram patterns
        # Medical scans often have bimodal or specific brightness distributions
        hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
        
        # Check if image has reasonable brightness range (not all black or all white)
        non_zero_bins = np.sum(hist > 0)
        if non_zero_bins < 50:  # Too few brightness levels
            return False, "Image appears to have limited brightness range. Medical scans typically have more variation."
        
        # Check 4: Aspect ratio - medical scans are often square or near-square
        width, height = image.size
        aspect_ratio = max(width, height) / min(width, height)
        
        # Very wide or tall images are less likely to be medical scans
        # Brain MRIs are typically square or near-square
        if aspect_ratio > 2.5:  # Stricter for brain MRI
            return False, "Image aspect ratio is unusual for a brain MRI scan. Brain MRI images are typically square or near-square."
        
        return True, ""
    
    except Exception as e:
        return False, f"Error analyzing image: {str(e)}"


def is_valid_image(file) -> Tuple[bool, str]:
    """
    Validate if the uploaded file is a valid medical image (MRI or X-ray).
    Returns (is_valid, error_message).
    """
    try:
        # Check file extension
        if not file.filename or not allowed_file(file.filename):
            return False, "Invalid file format. Please upload a JPG, PNG, or JPEG image."
        
        # Read image data
        file.seek(0)
        image_data = file.read()
        file.seek(0)  # Reset file pointer
        
        if len(image_data) == 0:
            return False, "Empty file. Please upload a valid image."
        
        # Try to open and validate image
        try:
            image = PILImage.open(io.BytesIO(image_data))
            image.verify()  # Verify it's a valid image
        except Exception:
            return False, "Invalid image file. The file may be corrupted or not a valid image format."
        
        # Reopen image for checks (verify() closes the image)
        image = PILImage.open(io.BytesIO(image_data))
        
        # Check image dimensions
        width, height = image.size
        if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
            return False, f"Image too small. Minimum size is {MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE} pixels."
        
        # Check if image is too large (optional, prevent memory issues)
        if width > 5000 or height > 5000:
            return False, "Image too large. Maximum size is 5000x5000 pixels."
        
        # Check if image has valid mode (RGB, RGBA, L, etc.)
        if image.mode not in ["RGB", "RGBA", "L", "P"]:
            return False, "Unsupported image mode. Please convert to RGB format."
        
        # Check if it's a medical image (MRI or X-ray)
        is_medical, medical_error = is_medical_image(image)
        if not is_medical:
            return False, medical_error
        
        return True, ""
    
    except Exception as e:
        return False, f"Error validating image: {str(e)}"


@app.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/results/<path:filename>")
def result_file(filename: str):
    return send_from_directory(RESULTS_FOLDER, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            return render_template("error.html", error_message="No file selected. Please upload an MRI image.")

        # Validate image
        is_valid, error_message = is_valid_image(file)
        if not is_valid:
            return render_template("error.html", error_message=error_message)

        try:
            filename = secure_filename(file.filename)
            upload_path = UPLOAD_FOLDER / filename
            file.save(upload_path)

            # Try to process the image
            try:
                image_tensor, _ = preprocess_image(str(upload_path))
                label, confidence = predict_image(MODEL, image_tensor, DEVICE)

                # Additional validation: Check if confidence is too low
                # Low confidence suggests the image might not be a brain MRI
                MIN_CONFIDENCE = 0.60  # 60% minimum confidence threshold
                if confidence < MIN_CONFIDENCE:
                    return render_template(
                        "error.html",
                        error_message=f"Image does not appear to be a brain MRI scan. The model confidence is too low ({confidence * 100:.1f}%). Please upload a clear brain MRI image."
                    )

                # Measure processing time
                start_time = time.time()
                overlay_path = explain(str(upload_path), str(MODEL_PATH))
                processing_time = time.time() - start_time

                # Get image dimensions
                image = PILImage.open(upload_path)
                image_size = f"{image.size[0]}x{image.size[1]}"

                # Generate enhanced explainability
                detailed_explanation = generate_detailed_explanation(
                    MODEL, image_tensor, label, confidence, DEVICE
                )
                model_decision = explain_model_decision(MODEL, image_tensor, DEVICE)

                # Get tumor information (educational)
                has_tumor = label == "Tumor"
                tumor_type_suggestions = get_tumor_type_suggestions(confidence, has_tumor)
                tumor_info = {}
                if tumor_type_suggestions:
                    # Get info for first suggested type
                    tumor_info = get_tumor_info(tumor_type_suggestions[0]) if tumor_type_suggestions else {}
                
                general_tumor_info = get_general_tumor_info()

                # Get recommended doctors
                recommended_doctors = get_recommended_doctors(has_tumor, confidence)

                # Save to database
                prediction_id = save_prediction(
                    filename=filename,
                    prediction=label,
                    confidence=confidence,
                    original_path=str(upload_path),
                    overlay_path=str(overlay_path),
                    image_size=image_size,
                    processing_time=round(processing_time, 2)
                )

                context = {
                    "prediction_id": prediction_id,
                    "prediction": label,
                    "confidence": f"{confidence * 100:.2f}",
                    "confidence_raw": confidence,
                    "original_url": url_for("uploaded_file", filename=filename),
                    "overlay_url": url_for("result_file", filename=Path(overlay_path).name),
                    "processing_time": round(processing_time, 2),
                    "detailed_explanation": detailed_explanation,
                    "model_decision": model_decision,
                    "tumor_info": tumor_info,
                    "tumor_type_suggestions": tumor_type_suggestions,
                    "general_tumor_info": general_tumor_info,
                    "recommended_doctors": recommended_doctors,
                    "has_tumor": has_tumor,
                }
                return render_template("result_enhanced.html", **context)
            
            except Exception as e:
                # If processing fails, it might not be a valid MRI image
                return render_template(
                    "error.html",
                    error_message=f"Unable to process image. This may not be a valid brain MRI scan. Please ensure you upload a clear brain MRI image. Error: {str(e)}"
                )
        
        except Exception as e:
            return render_template("error.html", error_message=f"Error processing file: {str(e)}")

    return render_template("upload.html")


@app.route("/history")
def history():
    """Display prediction history."""
    predictions = get_all_predictions(limit=100)
    return render_template("history.html", predictions=predictions)


@app.route("/statistics")
def statistics():
    """Display statistics about predictions."""
    stats = get_statistics()
    return render_template("statistics.html", stats=stats)


@app.route("/delete/<int:prediction_id>", methods=["POST"])
def delete_prediction_route(prediction_id: int):
    """Delete a prediction from history."""
    if delete_prediction(prediction_id):
        return redirect(url_for("history"))
    return render_template("error.html", error_message="Failed to delete prediction.")


@app.route("/doctors")
def doctors():
    """Display directory of specialist doctors."""
    all_doctors = get_all_doctors()
    return render_template("doctors.html", doctors=all_doctors)


@app.route("/tumor-info")
def tumor_info_page():
    """Display educational information about brain tumors."""
    all_tumor_info = get_tumor_info()
    general_info = get_general_tumor_info()
    return render_template("tumor_info.html", tumor_types=all_tumor_info, general_info=general_info)


if __name__ == "__main__":
    app.run(debug=True)


