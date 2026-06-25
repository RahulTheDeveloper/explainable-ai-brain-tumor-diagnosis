"""Database utilities for storing prediction history."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


DB_PATH = Path("predictions.db")


def init_database():
    """Initialize the SQLite database for storing predictions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            original_path TEXT,
            overlay_path TEXT,
            timestamp TEXT NOT NULL,
            image_size TEXT,
            processing_time REAL
        )
    """)
    
    conn.commit()
    conn.close()


def save_prediction(
    filename: str,
    prediction: str,
    confidence: float,
    original_path: str,
    overlay_path: str,
    image_size: Optional[str] = None,
    processing_time: Optional[float] = None
) -> int:
    """Save a prediction to the database."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO predictions 
        (filename, prediction, confidence, original_path, overlay_path, timestamp, image_size, processing_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (filename, prediction, confidence, original_path, overlay_path, timestamp, image_size, processing_time))
    
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return prediction_id


def get_all_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    """Get all predictions from the database."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM predictions 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_prediction_by_id(prediction_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific prediction by ID."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_statistics() -> Dict[str, Any]:
    """Get statistics about all predictions."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total predictions
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    
    # Predictions by class
    cursor.execute("""
        SELECT prediction, COUNT(*) as count 
        FROM predictions 
        GROUP BY prediction
    """)
    by_class = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Average confidence
    cursor.execute("SELECT AVG(confidence) FROM predictions")
    avg_confidence = cursor.fetchone()[0] or 0.0
    
    # High confidence predictions (>80%)
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE confidence > 0.8")
    high_confidence = cursor.fetchone()[0]
    
    # Recent predictions (last 24 hours)
    cursor.execute("""
        SELECT COUNT(*) FROM predictions 
        WHERE timestamp > datetime('now', '-1 day')
    """)
    recent = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "by_class": by_class,
        "avg_confidence": round(avg_confidence * 100, 2),
        "high_confidence_count": high_confidence,
        "recent_count": recent
    }


def delete_prediction(prediction_id: int) -> bool:
    """Delete a prediction from the database."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted

