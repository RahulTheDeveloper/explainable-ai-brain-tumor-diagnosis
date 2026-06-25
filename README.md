# Brain Tumor MRI Classification with Grad-CAM

A Flask web application for classifying brain MRI images and visualizing model predictions using Grad-CAM explainability.

## Features

### Core Features
- Brain MRI image classification (Tumor/No Tumor)
- Grad-CAM visualization to show which regions influenced the prediction
- Robust image validation for medical images
- Web-based interface for easy use

### Enhanced Features (New!)
- 📊 **Prediction History** - View all past predictions with details
- 📈 **Statistics Dashboard** - Track model performance and usage statistics
- 🖼️ **Image Preview** - Preview images before uploading
- 📊 **Confidence Visualization** - Visual confidence bars and charts
- ⏱️ **Processing Time Tracking** - See how long each prediction takes
- 🗑️ **History Management** - Delete old predictions
- 🔗 **Navigation** - Easy navigation between pages

## Setup Instructions

### 1. Install Dependencies

Make sure you have Python 3.9+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

Or if using the virtual environment in `app/venv`:

```bash
# Activate virtual environment
# On Windows:
app\venv\Scripts\activate

# On Linux/Mac:
source app/venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running in VS Code

#### Method 1: Using the Debugger (Recommended)

1. Open the project folder in VS Code
2. Press `F5` or go to **Run and Debug** (Ctrl+Shift+D)
3. Select **"Python: Flask App"** from the dropdown
4. Click the green play button or press `F5`
5. The app will start and you'll see the URL in the terminal (usually `http://127.0.0.1:5000/`)

#### Method 2: Using the Terminal

1. Open the integrated terminal in VS Code (Ctrl+`)
2. Activate the virtual environment (if using one):
   ```bash
   app\venv\Scripts\activate  # Windows
   # or
   source app/venv/bin/activate  # Linux/Mac
   ```
3. Run the Flask app:
   ```bash
   python app/app.py
   ```
4. Open your browser and go to `http://localhost:5000/`

#### Method 3: Using Flask Command

1. Set the Flask app environment variable:
   ```bash
   $env:FLASK_APP="app/app.py"  # PowerShell
   # or
   export FLASK_APP=app/app.py  # Linux/Mac
   ```
2. Run Flask:
   ```bash
   flask run
   ```

## Project Structure

```
python project/
├── app/
│   ├── app.py              # Main Flask application
│   ├── templates/          # HTML templates
│   │   ├── upload.html
│   │   ├── result.html
│   │   ├── error.html
│   │   ├── history.html    # Prediction history page
│   │   └── statistics.html # Statistics dashboard
│   └── venv/               # Virtual environment (optional)
├── src/
│   ├── predict.py          # Prediction functions
│   ├── explain.py          # Grad-CAM explanation functions
│   └── database.py          # Database operations for history
├── models/
│   └── best_model.pth      # Trained model weights
├── uploads/                 # Uploaded images (created automatically)
├── results/                 # Grad-CAM results (created automatically)
├── predictions.db           # SQLite database for history (created automatically)
├── requirements.txt         # Python dependencies
└── PROJECT_ENHANCEMENTS.md  # List of enhancement suggestions
```

## Usage

1. Start the Flask application
2. Open `http://localhost:5000/` in your browser
3. Upload a brain MRI image (JPG, PNG, or JPEG)
4. Preview the image before uploading (new!)
5. View the classification result and Grad-CAM visualization
6. Check your prediction history at `/history`
7. View statistics at `/statistics`

## New Pages

- **`/`** - Main upload page with image preview
- **`/history`** - View all past predictions
- **`/statistics`** - Statistics dashboard with charts

## Requirements

- Python 3.9+
- Flask
- PyTorch
- Torchvision
- Pillow (PIL)
- NumPy
- Matplotlib
- Captum (for Grad-CAM)

## Notes

- The model requires a trained `best_model.pth` file in the `models/` directory
- Images are validated to ensure they are grayscale medical images
- Minimum confidence threshold is 60% for predictions
- The app automatically creates `uploads/`, `results/`, and `predictions.db` (database) directories/files
- All predictions are automatically saved to the database for history tracking

## Future Enhancements

See `PROJECT_ENHANCEMENTS.md` for a comprehensive list of suggested improvements including:
- Batch processing
- PDF report generation
- REST API endpoints
- Docker support
- And much more!


