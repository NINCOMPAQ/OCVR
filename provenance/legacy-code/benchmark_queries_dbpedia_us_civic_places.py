DBO = "http://dbpedia.org/ontology/"


def cls(name: str) -> str:
    return f"{DBO}{name}"


TESTS = [
    {"name": "University in California", "query": "university in California", "constraint_any": [cls("University")]},
    {"name": "University in Texas", "query": "university in Texas", "constraint_any": [cls("University")]},
    {"name": "Public university", "query": "public university in the United States", "constraint_any": [cls("University")]},
    {"name": "Catholic university", "query": "Catholic university in America", "constraint_any": [cls("University")]},

    {"name": "High school", "query": "high school in the United States", "constraint_any": [cls("School")]},
    {"name": "School in New York", "query": "school in New York", "constraint_any": [cls("School")]},
    {"name": "Preparatory school", "query": "preparatory school", "constraint_any": [cls("School")]},
    {"name": "Elementary school", "query": "elementary school", "constraint_any": [cls("School")]},

    {"name": "City in California", "query": "city in California", "constraint_any": [cls("City")]},
    {"name": "City in Texas", "query": "city in Texas", "constraint_any": [cls("City")]},
    {"name": "City in Florida", "query": "city in Florida", "constraint_any": [cls("City")]},
    {"name": "Large city", "query": "large city in the United States", "constraint_any": [cls("City")]},

    {"name": "Town in Massachusetts", "query": "town in Massachusetts", "constraint_any": [cls("Town")]},
    {"name": "Town in New England", "query": "town in New England", "constraint_any": [cls("Town")]},
    {"name": "County town", "query": "small town in the United States", "constraint_any": [cls("Town")]},
    {"name": "Historic town", "query": "historic town", "constraint_any": [cls("Town")]},

    {"name": "Village in Ohio", "query": "village in Ohio", "constraint_any": [cls("Village")]},
    {"name": "Village in Illinois", "query": "village in Illinois", "constraint_any": [cls("Village")]},
    {"name": "Village in New York", "query": "village in New York", "constraint_any": [cls("Village")]},
    {"name": "Small village", "query": "small village in America", "constraint_any": [cls("Village")]},

    {"name": "Historic building", "query": "historic building in the United States", "constraint_any": [cls("Building")]},
    {"name": "Government building", "query": "government building", "constraint_any": [cls("Building")]},
    {"name": "Building in Chicago", "query": "building in Chicago", "constraint_any": [cls("Building")]},
    {"name": "Library building", "query": "library building", "constraint_any": [cls("Building"), cls("Library")]},

    {"name": "Church", "query": "church in the United States", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Cathedral", "query": "cathedral in America", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Synagogue", "query": "synagogue in the United States", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Religious building", "query": "religious building", "constraint_any": [cls("ReligiousBuilding")]},

    {"name": "Dam in California", "query": "dam in California", "constraint_any": [cls("Dam")]},
    {"name": "Hydroelectric dam", "query": "hydroelectric dam", "constraint_any": [cls("Dam")]},
    {"name": "Dam on river", "query": "dam on a river", "constraint_any": [cls("Dam")]},

    {"name": "Stadium", "query": "stadium in the United States", "constraint_any": [cls("Stadium")]},
    {"name": "Football stadium", "query": "football stadium", "constraint_any": [cls("Stadium")]},
    {"name": "Baseball stadium", "query": "baseball stadium", "constraint_any": [cls("Stadium")]},
    {"name": "Sports venue", "query": "sports venue", "constraint_any": [cls("Venue"), cls("Stadium")]},

    {"name": "Library", "query": "public library", "constraint_any": [cls("Library")]},
    {"name": "University library", "query": "university library", "constraint_any": [cls("Library")]},
    {"name": "Hospital", "query": "hospital in the United States", "constraint_any": [cls("Hospital")]},
    {"name": "Medical center", "query": "medical center", "constraint_any": [cls("Hospital")]},

    {"name": "Educational institution broad", "query": "educational institution in the United States", "constraint_any": [cls("EducationalInstitution")]},
    {"name": "Civic venue broad", "query": "venue in the United States", "constraint_any": [cls("Venue")]},
    {"name": "Civic building broad", "query": "civic building in America", "constraint_any": [cls("Building"), cls("ArchitecturalStructure")]},
]
