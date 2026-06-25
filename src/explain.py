"""Grad-CAM explainability utilities for Brain Tumor MRI Classification."""

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from captum.attr import LayerGradCam
from PIL import Image
from torchvision import transforms
from torchvision.models import ResNet18_Weights, resnet18


IMAGE_SIZE: int = 224


def build_model(num_classes: int = 2, device: torch.device | str = "cpu") -> nn.Module:
    """Create the ResNet18 model architecture used for Grad-CAM."""

    model = resnet18(weights=ResNet18_Weights.DEFAULT)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    model.to(device)
    model.eval()
    return model


def load_model(model_path: str, device: torch.device | str = "cpu") -> nn.Module:
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model weights not found at '{model_path}'. Train the model before running Grad-CAM."
        )

    model = build_model(device=device)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def preprocess_image(image_path: str) -> Tuple[torch.Tensor, np.ndarray]:
    """Preprocess the image and return both tensor and original numpy image."""

    transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    image = Image.open(image_path).convert("RGB")
    original = np.array(image)
    tensor = transform(image).unsqueeze(0)
    return tensor, original


def generate_gradcam(
    model: nn.Module, image_tensor: torch.Tensor, target_layer: nn.Module, device: torch.device
) -> np.ndarray:
    """Generate Grad-CAM heatmap for the provided image tensor."""

    image_tensor = image_tensor.to(device)
    image_tensor.requires_grad = True

    grad_cam = LayerGradCam(model, target_layer)
    # Determine the target class from model prediction
    with torch.no_grad():
        logits = model(image_tensor)
        predicted_idx = torch.argmax(logits, dim=1)

    attribution = grad_cam.attribute(image_tensor, target=predicted_idx)

    # Convert attribution to numpy and ensure it's 2D
    if isinstance(attribution, torch.Tensor):
        attribution = attribution.cpu().detach().numpy()
    
    # Handle different attribution shapes - use squeeze to remove dimensions of size 1
    # Then ensure we have a 2D array
    while len(attribution.shape) > 2:
        if attribution.shape[0] == 1:
            attribution = np.squeeze(attribution, axis=0)
        elif len(attribution.shape) == 4 and attribution.shape[1] > 1:
            # (batch, channels, H, W) - average across channels
            attribution = attribution[0].mean(axis=0)
        elif len(attribution.shape) == 3:
            # (batch, H, W) or (channels, H, W) - take first or average
            if attribution.shape[0] == 1:
                attribution = attribution[0]
            else:
                attribution = attribution.mean(axis=0)
        else:
            # Try to squeeze any dimension of size 1
            attribution = np.squeeze(attribution)
            if len(attribution.shape) > 2:
                # If still not 2D, take mean across first dimension
                attribution = attribution.mean(axis=0)
    
    # Final check - ensure it's 2D
    if len(attribution.shape) != 2:
        raise ValueError(f"Attribution should be 2D after processing, got shape: {attribution.shape}")
    
    # Resize to IMAGE_SIZE if needed
    if attribution.shape[0] != IMAGE_SIZE or attribution.shape[1] != IMAGE_SIZE:
        from PIL import Image as PILImage
        attribution_pil = PILImage.fromarray((attribution * 255).astype(np.uint8))
        attribution_pil = attribution_pil.resize((IMAGE_SIZE, IMAGE_SIZE))
        attribution = np.array(attribution_pil).astype(np.float32) / 255.0
    
    heatmap = attribution

    # Normalize heatmap
    if heatmap.max() > heatmap.min():
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)
    
    return heatmap


def overlay_heatmap(original_image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """Overlay the heatmap on the original image."""

    # Resize original image to match heatmap size
    from PIL import Image as PILImage
    original_resized = np.array(PILImage.fromarray(original_image).resize((IMAGE_SIZE, IMAGE_SIZE)))
    
    heatmap_colored = plt.get_cmap("jet")(heatmap)[..., :3]  # Remove alpha channel
    heatmap_colored = (heatmap_colored * 255).astype(np.uint8)

    overlay = (alpha * heatmap_colored + (1 - alpha) * original_resized).astype(np.uint8)
    return overlay


def save_results(original: np.ndarray, heatmap: np.ndarray, overlay: np.ndarray, output_path: Path) -> None:
    """Save Grad-CAM results to the specified output path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(original)
    axes[0].axis("off")
    axes[0].set_title("Original Image")

    axes[1].imshow(heatmap, cmap="jet")
    axes[1].axis("off")
    axes[1].set_title("Grad-CAM Heatmap")

    axes[2].imshow(overlay)
    axes[2].axis("off")
    axes[2].set_title("Overlay")

    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def explain(image_path: str, model_path: str = os.path.join("models", "best_model.pth")) -> Path:
    """Generate Grad-CAM explanation for a given image and return the saved path."""

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image '{image_path}' not found.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path, device=device)

    image_tensor, original_image = preprocess_image(image_path)

    # Use the last convolutional layer of ResNet18 for Grad-CAM
    target_layer = model.layer4[-1].conv2
    heatmap = generate_gradcam(model, image_tensor, target_layer, device)

    overlay = overlay_heatmap(original_image, heatmap)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gradcam_{Path(image_path).stem}_{timestamp}.png"
    output_path = Path("results") / filename

    save_results(original_image, heatmap, overlay, output_path)
    return output_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grad-CAM explanation for brain tumor MRI classification")
    parser.add_argument("image", help="Path to the MRI image")
    parser.add_argument(
        "--model-path",
        default=os.path.join("models", "best_model.pth"),
        help="Path to trained model weights (default: models/best_model.pth)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output_path = explain(args.image, args.model_path)
    print(f"Grad-CAM saved to: {output_path}")


if __name__ == "__main__":
    main()


