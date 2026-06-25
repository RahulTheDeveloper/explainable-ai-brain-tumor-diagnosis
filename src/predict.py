"""Prediction functions for Brain Tumor MRI Classification."""

import torch
import torch.nn as nn
from typing import Tuple


# Import functions from explain module
from explain import load_model, preprocess_image


def predict_image(model: nn.Module, image_tensor: torch.Tensor, device: torch.device) -> Tuple[str, float]:
    """
    Predict the class of an image using the provided model.
    
    Args:
        model: PyTorch model for prediction
        image_tensor: Preprocessed image tensor
        device: Device to run the model on (cpu or cuda)
    
    Returns:
        Tuple of (predicted_class, confidence_score)
        - predicted_class: "Tumor" or "No Tumor"
        - confidence_score: Float between 0 and 1
    """
    model.eval()
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        predicted_idx = int(torch.argmax(probabilities, dim=1).item())
        confidence = probabilities[0][predicted_idx].item()
    
    # Map index to class label
    # Assuming: 0 = "No Tumor", 1 = "Tumor"
    class_labels = ["No Tumor", "Tumor"]
    predicted_class = class_labels[predicted_idx] if predicted_idx < len(class_labels) else "Unknown"
    
    return predicted_class, confidence


__all__ = ["predict_image", "load_model", "preprocess_image"]
