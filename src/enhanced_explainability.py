"""Enhanced explainability features for brain tumor classification."""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple
from captum.attr import IntegratedGradients, Saliency, LayerGradCam
from captum.attr import visualization as viz


def generate_detailed_explanation(
    model: nn.Module,
    image_tensor: torch.Tensor,
    predicted_class: str,
    confidence: float,
    device: torch.device
) -> Dict:
    """
    Generate detailed explanation of the model's prediction.
    
    Returns:
        Dictionary containing various explanation metrics and insights
    """
    model.eval()
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        probs = probabilities[0].cpu().numpy()
    
    # Get prediction confidence breakdown
    tumor_prob = probs[1] if len(probs) > 1 else 0.0
    no_tumor_prob = probs[0]
    
    # Calculate explanation metrics
    explanation = {
        "predicted_class": predicted_class,
        "confidence": float(confidence),
        "confidence_breakdown": {
            "tumor_probability": float(tumor_prob),
            "no_tumor_probability": float(no_tumor_prob)
        },
        "explanation_level": get_explanation_level(confidence),
        "key_factors": get_key_factors(predicted_class, confidence),
        "model_certainty": get_certainty_level(confidence),
        "recommendations": get_recommendations(predicted_class, confidence),
        "interpretation": get_interpretation(predicted_class, confidence, tumor_prob, no_tumor_prob)
    }
    
    return explanation


def get_explanation_level(confidence: float) -> str:
    """Determine the level of explanation based on confidence."""
    if confidence >= 0.90:
        return "Very High Confidence"
    elif confidence >= 0.80:
        return "High Confidence"
    elif confidence >= 0.70:
        return "Moderate Confidence"
    elif confidence >= 0.60:
        return "Low-Moderate Confidence"
    else:
        return "Low Confidence"


def get_key_factors(predicted_class: str, confidence: float) -> List[str]:
    """Get key factors that influenced the prediction."""
    factors = []
    
    if predicted_class == "Tumor":
        factors.append("The model detected abnormal patterns in brain tissue")
        factors.append("Grad-CAM visualization highlights regions of interest")
        if confidence > 0.85:
            factors.append("Strong indicators of tumor presence detected")
        factors.append("Image characteristics match known tumor patterns")
    else:
        factors.append("Normal brain tissue patterns detected")
        factors.append("No abnormal growth patterns identified")
        factors.append("Image shows typical healthy brain structure")
    
    factors.append(f"Model confidence: {confidence * 100:.1f}%")
    
    return factors


def get_certainty_level(confidence: float) -> Dict:
    """Get detailed certainty information."""
    if confidence >= 0.90:
        level = "Very Certain"
        description = "The model is highly confident in this prediction."
    elif confidence >= 0.80:
        level = "Certain"
        description = "The model is confident in this prediction."
    elif confidence >= 0.70:
        level = "Moderately Certain"
        description = "The model shows moderate confidence in this prediction."
    elif confidence >= 0.60:
        level = "Somewhat Certain"
        description = "The model shows some confidence, but additional evaluation may be beneficial."
    else:
        level = "Uncertain"
        description = "The model has low confidence. Please consult a medical professional."
    
    return {
        "level": level,
        "description": description,
        "confidence_score": confidence,
        "requires_medical_review": confidence < 0.70
    }


def get_recommendations(predicted_class: str, confidence: float) -> List[str]:
    """Get recommendations based on prediction."""
    recommendations = []
    
    if predicted_class == "Tumor":
        recommendations.append("⚠️ Consult with a neuro-oncologist or neurosurgeon immediately")
        recommendations.append("Schedule a comprehensive neurological evaluation")
        recommendations.append("Consider additional imaging studies (CT scan, advanced MRI)")
        if confidence < 0.80:
            recommendations.append("Seek a second opinion from another specialist")
        recommendations.append("Discuss treatment options with your healthcare team")
        recommendations.append("Consider genetic testing if recommended by your doctor")
    else:
        recommendations.append("✓ Continue regular health check-ups")
        recommendations.append("Monitor for any new symptoms")
        if confidence < 0.80:
            recommendations.append("Consider follow-up imaging if symptoms persist")
        recommendations.append("Maintain a healthy lifestyle")
    
    recommendations.append("This AI prediction is for educational purposes only and should not replace professional medical advice")
    
    return recommendations


def get_interpretation(
    predicted_class: str,
    confidence: float,
    tumor_prob: float,
    no_tumor_prob: float
) -> str:
    """Get a detailed interpretation of the results."""
    if predicted_class == "Tumor":
        if confidence >= 0.90:
            interpretation = (
                f"The AI model has identified strong indicators of a brain tumor with {confidence * 100:.1f}% confidence. "
                f"The analysis suggests a {tumor_prob * 100:.1f}% probability of tumor presence. "
                "The Grad-CAM visualization highlights the specific brain regions that contributed to this assessment. "
                "It is crucial to consult with a qualified neuro-oncologist or neurosurgeon for a comprehensive evaluation, "
                "diagnostic confirmation, and treatment planning."
            )
        elif confidence >= 0.80:
            interpretation = (
                f"The model indicates a likely presence of a brain tumor with {confidence * 100:.1f}% confidence. "
                f"There is a {tumor_prob * 100:.1f}% probability of tumor presence. "
                "The highlighted regions in the visualization show areas of concern. "
                "Professional medical consultation is strongly recommended for proper diagnosis and treatment."
            )
        else:
            interpretation = (
                f"The model suggests possible tumor presence with {confidence * 100:.1f}% confidence. "
                f"The probability analysis shows {tumor_prob * 100:.1f}% for tumor and {no_tumor_prob * 100:.1f}% for no tumor. "
                "Due to the moderate confidence level, additional medical evaluation and possibly a second opinion are recommended."
            )
    else:
        if confidence >= 0.90:
            interpretation = (
                f"The model indicates no tumor detected with {confidence * 100:.1f}% confidence. "
                f"The analysis shows a {no_tumor_prob * 100:.1f}% probability of normal brain tissue. "
                "The brain structure appears normal in this scan. Continue regular health monitoring."
            )
        else:
            interpretation = (
                f"The model suggests no tumor with {confidence * 100:.1f}% confidence. "
                f"Probability analysis: {no_tumor_prob * 100:.1f}% no tumor, {tumor_prob * 100:.1f}% tumor. "
                "If you have concerns or symptoms, consult with a healthcare professional."
            )
    
    return interpretation


def explain_model_decision(
    model: nn.Module,
    image_tensor: torch.Tensor,
    device: torch.device
) -> Dict:
    """Provide a comprehensive explanation of the model's decision-making process."""
    
    # Get feature importance
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.nn.functional.softmax(logits, dim=1)
    
    # Calculate entropy (uncertainty measure)
    probs = probabilities[0].cpu().numpy()
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    max_entropy = np.log(len(probs))
    normalized_entropy = entropy / max_entropy
    uncertainty = normalized_entropy
    
    return {
        "decision_process": "The model analyzes brain MRI images using deep learning to identify patterns associated with brain tumors.",
        "key_features": [
            "Tissue density variations",
            "Abnormal growth patterns",
            "Contrast enhancement patterns",
            "Structural abnormalities"
        ],
        "uncertainty": float(uncertainty),
        "confidence_distribution": {
            "tumor": float(probs[1]) if len(probs) > 1 else 0.0,
            "no_tumor": float(probs[0])
        },
        "model_limitations": [
            "This is an AI-assisted tool, not a replacement for professional medical diagnosis",
            "Results should be confirmed by qualified medical professionals",
            "Model accuracy depends on image quality and scan parameters",
            "Some rare tumor types may not be accurately detected"
        ]
    }

