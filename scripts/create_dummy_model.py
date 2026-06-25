from pathlib import Path
import sys
import os

# Ensure src is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    import torch
    from explain import build_model
except Exception as e:
    print("This script requires PyTorch and the project's src package to be importable.")
    print("Run it inside your virtual environment after installing dependencies.")
    raise

models_dir = PROJECT_ROOT / "models"
models_dir.mkdir(parents=True, exist_ok=True)

print("Building ResNet18 model (random-initialized)...")    
model = build_model(device="cpu")

save_path = models_dir / "best_model.pth"
torch.save(model.state_dict(), save_path)
print(f"Saved dummy model weights to: {save_path}")
