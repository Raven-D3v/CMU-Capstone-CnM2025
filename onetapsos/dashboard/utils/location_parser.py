# dashboard/utils/location_parser.py

def parse_location(location_str):
    """
    Parse location string into structured components.
    Assumes format like: 'M F Gozon, Barangay Catmon, Malabon, Metro Manila, Philippines'
    """
    if not location_str:
        return {
            "thoroughfare": None,
            "subLocality": None,
            "locality": None,
            "adminArea": None,
            "countryName": None,
        }

    parts = [p.strip() for p in location_str.split(",")]
    return {
        "thoroughfare": parts[0] if len(parts) > 0 else None,
        "subLocality": parts[1] if len(parts) > 1 else None,
        "locality": parts[2] if len(parts) > 2 else None,
        "adminArea": parts[3] if len(parts) > 3 else None,
        "countryName": parts[4] if len(parts) > 4 else None,
    }
