"""
Reef location configurations for the Andaman Islands monitoring system.
"""

REEF_LOCATIONS = [
    {
        "id": "jolly-buoy",
        "name": "Jolly_Buoy",
        "lat": 11.495,
        "lon": 92.610,
        "description": "Primary monitoring site"
    },
    {
        "id": "neel-islands", 
        "name": "Neel Islands",
        "lat": 11.832919,
        "lon": 93.052612,
        "description": "Northern reef system"
    },
    {
        "id": "mahatma-gandhi",
        "name": "Mahatma Gandhi Marine National Park", 
        "lat": 11.5690,
        "lon": 92.6542,
        "description": "Protected marine area"
    },
    {
        "id": "havelock",
        "name": "Havelock",
        "lat": 11.960000,
        "lon": 93.000000,
        "description": "Tourist diving area"
    }
]

# Bleaching threshold temperature (°C)
BLEACHING_THRESHOLD = 29.0

# DHW (Degree Heating Weeks) thresholds
DHW_THRESHOLDS = {
    "low": 4.0,
    "moderate": 8.0,
    "high": 12.0
}

def get_location_by_id(location_id: str):
    """Get location configuration by ID."""
    for location in REEF_LOCATIONS:
        if location["id"] == location_id:
            return location
    return None

def get_risk_level(dhw: float) -> str:
    """Determine risk level based on DHW value."""
    if dhw < DHW_THRESHOLDS["low"]:
        return "low"
    elif dhw < DHW_THRESHOLDS["moderate"]:
        return "moderate"
    elif dhw < DHW_THRESHOLDS["high"]:
        return "high"
    else:
        return "severe"