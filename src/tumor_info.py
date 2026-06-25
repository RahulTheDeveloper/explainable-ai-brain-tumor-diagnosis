"""Tumor information and educational content."""

from typing import Dict, List, Optional


TUMOR_TYPES = {
    "Glioma": {
        "name": "Glioma",
        "description": "Gliomas are tumors that arise from glial cells in the brain. They are the most common type of primary brain tumor.",
        "types": [
            "Astrocytoma - Arises from astrocytes",
            "Oligodendroglioma - Arises from oligodendrocytes",
            "Ependymoma - Arises from ependymal cells"
        ],
        "symptoms": [
            "Headaches",
            "Seizures",
            "Memory problems",
            "Personality changes",
            "Vision problems",
            "Speech difficulties"
        ],
        "severity": "Varies by grade (I-IV), with Grade IV (Glioblastoma) being the most aggressive",
        "treatment_approaches": [
            "Surgery to remove as much tumor as possible",
            "Radiation therapy",
            "Chemotherapy",
            "Targeted therapy",
            "Immunotherapy (for some types)"
        ],
        "prognosis": "Depends on tumor grade, location, and patient age. Grade I-II have better prognosis than Grade III-IV."
    },
    "Meningioma": {
        "name": "Meningioma",
        "description": "Meningiomas are tumors that arise from the meninges, the membranes surrounding the brain and spinal cord. Most are benign (non-cancerous).",
        "types": [
            "Grade I (Benign) - Most common, slow-growing",
            "Grade II (Atypical) - Faster growing",
            "Grade III (Anaplastic) - Malignant, rare"
        ],
        "symptoms": [
            "Headaches",
            "Seizures",
            "Weakness in arms or legs",
            "Vision changes",
            "Hearing loss or ringing in ears",
            "Memory problems"
        ],
        "severity": "Most are benign and slow-growing",
        "treatment_approaches": [
            "Observation (for small, asymptomatic tumors)",
            "Surgical removal",
            "Radiation therapy (for inoperable or residual tumors)",
            "Stereotactic radiosurgery"
        ],
        "prognosis": "Excellent for Grade I meningiomas. Most patients have good outcomes with complete surgical removal."
    },
    "Pituitary Adenoma": {
        "name": "Pituitary Adenoma",
        "description": "Tumors that develop in the pituitary gland, a small gland at the base of the brain that controls hormone production.",
        "types": [
            "Functioning adenomas - Produce hormones",
            "Non-functioning adenomas - Do not produce hormones"
        ],
        "symptoms": [
            "Vision problems (especially peripheral vision)",
            "Headaches",
            "Hormonal imbalances",
            "Fatigue",
            "Weight changes",
            "Menstrual irregularities"
        ],
        "severity": "Most are benign, but can cause significant symptoms",
        "treatment_approaches": [
            "Medication (for hormone-producing tumors)",
            "Surgical removal (transsphenoidal surgery)",
            "Radiation therapy",
            "Observation for small, non-functioning tumors"
        ],
        "prognosis": "Generally good, especially with early treatment. Most can be successfully treated."
    },
    "Schwannoma": {
        "name": "Schwannoma (Acoustic Neuroma)",
        "description": "Benign tumors that arise from Schwann cells, often affecting the vestibular nerve (acoustic neuroma).",
        "types": [
            "Vestibular schwannoma (most common)",
            "Trigeminal schwannoma",
            "Other cranial nerve schwannomas"
        ],
        "symptoms": [
            "Hearing loss (usually one-sided)",
            "Tinnitus (ringing in ears)",
            "Balance problems",
            "Facial numbness or weakness",
            "Headaches"
        ],
        "severity": "Usually benign and slow-growing",
        "treatment_approaches": [
            "Observation (for small tumors)",
            "Surgical removal",
            "Stereotactic radiosurgery",
            "Hearing preservation techniques"
        ],
        "prognosis": "Very good. Most schwannomas are successfully treated with minimal complications."
    },
    "Metastatic Brain Tumor": {
        "name": "Metastatic Brain Tumor",
        "description": "Cancer that has spread to the brain from another part of the body. Common sources include lung, breast, colon, and kidney cancers.",
        "types": [
            "Single metastasis",
            "Multiple metastases"
        ],
        "symptoms": [
            "Headaches",
            "Seizures",
            "Neurological deficits",
            "Cognitive changes",
            "Nausea and vomiting"
        ],
        "severity": "Depends on primary cancer type and extent of spread",
        "treatment_approaches": [
            "Surgery (for accessible single metastases)",
            "Whole brain radiation therapy",
            "Stereotactic radiosurgery",
            "Chemotherapy",
            "Targeted therapy",
            "Immunotherapy"
        ],
        "prognosis": "Varies significantly based on primary cancer type, number of metastases, and patient's overall health."
    }
}


def get_tumor_info(tumor_type: Optional[str] = None) -> Dict:
    """Get information about a specific tumor type or all tumor types."""
    if tumor_type and tumor_type in TUMOR_TYPES:
        return TUMOR_TYPES[tumor_type]
    return TUMOR_TYPES


def get_general_tumor_info() -> Dict:
    """Get general information about brain tumors."""
    return {
        "overview": "Brain tumors can be primary (originating in the brain) or secondary (metastatic, spreading from other organs).",
        "common_types": list(TUMOR_TYPES.keys()),
        "importance_of_early_detection": "Early detection and treatment significantly improve outcomes for brain tumor patients.",
        "diagnostic_methods": [
            "MRI scans",
            "CT scans",
            "Biopsy",
            "Neurological examination"
        ],
        "warning_signs": [
            "Persistent headaches",
            "Seizures",
            "Vision or hearing problems",
            "Balance issues",
            "Personality or behavior changes",
            "Memory problems"
        ]
    }


def get_tumor_type_suggestions(confidence: float, has_tumor: bool) -> List[str]:
    """Get suggested tumor types based on prediction (educational purposes)."""
    if not has_tumor:
        return []
    
    # Based on confidence, suggest most common types
    suggestions = []
    if confidence > 0.85:
        suggestions = ["Glioma", "Meningioma", "Pituitary Adenoma"]
    elif confidence > 0.70:
        suggestions = ["Glioma", "Meningioma"]
    else:
        suggestions = ["Various types possible - consult specialist"]
    
    return suggestions

