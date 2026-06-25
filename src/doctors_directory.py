"""Directory of specialist doctors for brain tumor treatment."""

from typing import List, Dict, Optional


SPECIALIST_DOCTORS = [
    {
        "id": 1,
        "name": "Dr. Sarah Johnson",
        "specialization": "Neuro-oncologist",
        "qualifications": "MD, PhD in Neuro-oncology",
        "hospital": "City General Hospital",
        "location": "New York, NY",
        "contact": "+1 (555) 123-4567",
        "email": "sarah.johnson@hospital.com",
        "experience_years": 15,
        "expertise": ["Glioma", "Glioblastoma", "Brain Metastases"],
        "languages": ["English", "Spanish"],
        "rating": 4.8,
        "consultation_fee": "$300",
        "availability": "Mon-Fri, 9 AM - 5 PM"
    },
    {
        "id": 2,
        "name": "Dr. Michael Chen",
        "specialization": "Neurosurgeon",
        "qualifications": "MD, FACS, Board Certified Neurosurgeon",
        "hospital": "Memorial Medical Center",
        "location": "Los Angeles, CA",
        "contact": "+1 (555) 234-5678",
        "email": "m.chen@memorialmc.com",
        "experience_years": 20,
        "expertise": ["Meningioma", "Pituitary Adenoma", "Schwannoma"],
        "languages": ["English", "Mandarin"],
        "rating": 4.9,
        "consultation_fee": "$350",
        "availability": "Mon-Thu, 8 AM - 4 PM"
    },
    {
        "id": 3,
        "name": "Dr. Emily Rodriguez",
        "specialization": "Radiation Oncologist",
        "qualifications": "MD, Radiation Oncology Specialist",
        "hospital": "University Medical Center",
        "location": "Chicago, IL",
        "contact": "+1 (555) 345-6789",
        "email": "e.rodriguez@umc.edu",
        "experience_years": 12,
        "expertise": ["Radiation Therapy", "Stereotactic Radiosurgery", "All Brain Tumor Types"],
        "languages": ["English", "Spanish", "French"],
        "rating": 4.7,
        "consultation_fee": "$280",
        "availability": "Tue-Fri, 10 AM - 6 PM"
    },
    {
        "id": 4,
        "name": "Dr. James Wilson",
        "specialization": "Neuro-oncologist & Neurosurgeon",
        "qualifications": "MD, PhD, Dual Board Certified",
        "hospital": "National Brain Tumor Institute",
        "location": "Boston, MA",
        "contact": "+1 (555) 456-7890",
        "email": "j.wilson@nbti.org",
        "experience_years": 18,
        "expertise": ["Complex Brain Tumors", "Pediatric Brain Tumors", "Research & Clinical Trials"],
        "languages": ["English"],
        "rating": 4.9,
        "consultation_fee": "$400",
        "availability": "Mon-Wed, 9 AM - 3 PM"
    },
    {
        "id": 5,
        "name": "Dr. Priya Patel",
        "specialization": "Neuro-oncologist",
        "qualifications": "MD, Neuro-oncology Fellowship",
        "hospital": "Regional Cancer Center",
        "location": "Houston, TX",
        "contact": "+1 (555) 567-8901",
        "email": "p.patel@rcc.org",
        "experience_years": 10,
        "expertise": ["Glioma", "Metastatic Brain Tumors", "Immunotherapy"],
        "languages": ["English", "Hindi", "Gujarati"],
        "rating": 4.6,
        "consultation_fee": "$275",
        "availability": "Mon-Fri, 8 AM - 5 PM"
    },
    {
        "id": 6,
        "name": "Dr. Robert Anderson",
        "specialization": "Neurosurgeon",
        "qualifications": "MD, Minimally Invasive Neurosurgery Specialist",
        "hospital": "Advanced Neurosurgical Center",
        "location": "Seattle, WA",
        "contact": "+1 (555) 678-9012",
        "email": "r.anderson@anc.com",
        "experience_years": 14,
        "expertise": ["Minimally Invasive Surgery", "Pituitary Tumors", "Skull Base Surgery"],
        "languages": ["English"],
        "rating": 4.8,
        "consultation_fee": "$320",
        "availability": "Tue-Thu, 9 AM - 4 PM"
    },
    {
        "id": 7,
        "name": "Dr. Lisa Thompson",
        "specialization": "Pediatric Neuro-oncologist",
        "qualifications": "MD, Pediatric Neuro-oncology Board Certified",
        "hospital": "Children's Hospital",
        "location": "Philadelphia, PA",
        "contact": "+1 (555) 789-0123",
        "email": "l.thompson@childrenshosp.org",
        "experience_years": 11,
        "expertise": ["Pediatric Brain Tumors", "Medulloblastoma", "Ependymoma"],
        "languages": ["English"],
        "rating": 4.9,
        "consultation_fee": "$300",
        "availability": "Mon-Fri, 8 AM - 5 PM"
    },
    {
        "id": 8,
        "name": "Dr. David Kim",
        "specialization": "Neuro-oncologist",
        "qualifications": "MD, Neuro-oncology & Clinical Research",
        "hospital": "Metropolitan Medical Center",
        "location": "San Francisco, CA",
        "contact": "+1 (555) 890-1234",
        "email": "d.kim@metrohealth.org",
        "experience_years": 13,
        "expertise": ["Glioblastoma", "Targeted Therapy", "Clinical Trials"],
        "languages": ["English", "Korean"],
        "rating": 4.7,
        "consultation_fee": "$290",
        "availability": "Mon, Wed, Fri, 9 AM - 5 PM"
    }
]


def get_all_doctors() -> List[Dict]:
    """Get all specialist doctors."""
    return SPECIALIST_DOCTORS


def get_doctors_by_specialization(specialization: str) -> List[Dict]:
    """Get doctors filtered by specialization."""
    return [doc for doc in SPECIALIST_DOCTORS if specialization.lower() in doc["specialization"].lower()]


def get_doctors_by_expertise(tumor_type: str) -> List[Dict]:
    """Get doctors who specialize in treating a specific tumor type."""
    matching_doctors = []
    for doc in SPECIALIST_DOCTORS:
        for expertise in doc["expertise"]:
            if tumor_type.lower() in expertise.lower() or expertise.lower() in tumor_type.lower():
                matching_doctors.append(doc)
                break
    return matching_doctors if matching_doctors else SPECIALIST_DOCTORS[:3]  # Return top 3 if no match


def get_doctor_by_id(doctor_id: int) -> Optional[Dict]:
    """Get a specific doctor by ID."""
    for doc in SPECIALIST_DOCTORS:
        if doc["id"] == doctor_id:
            return doc
    return None


def get_recommended_doctors(has_tumor: bool, confidence: float) -> List[Dict]:
    """Get recommended doctors based on prediction results."""
    if not has_tumor:
        return []  # No doctors needed if no tumor
    
    # Return top-rated doctors for consultation
    sorted_doctors = sorted(SPECIALIST_DOCTORS, key=lambda x: x["rating"], reverse=True)
    return sorted_doctors[:5]  # Top 5 rated doctors

