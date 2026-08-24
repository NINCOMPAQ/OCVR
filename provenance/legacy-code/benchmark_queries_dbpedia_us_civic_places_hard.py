DBO = "http://dbpedia.org/ontology/"


def cls(name: str) -> str:
    return f"{DBO}{name}"


TESTS = [
    {"name": "Campus in California", "query": "campus in California", "constraint_any": [cls("University")]},
    {"name": "State college", "query": "state college", "constraint_any": [cls("University")]},
    {"name": "Liberal arts college", "query": "liberal arts college", "constraint_any": [cls("University")]},
    {"name": "Graduate school", "query": "graduate school of management", "constraint_any": [cls("University")]},

    {"name": "Central High", "query": "Central High", "constraint_any": [cls("School")]},
    {"name": "Academy in New York", "query": "academy in New York", "constraint_any": [cls("School")]},
    {"name": "Prep school", "query": "prep school", "constraint_any": [cls("School")]},
    {"name": "Elementary in California", "query": "elementary in California", "constraint_any": [cls("School")]},

    {"name": "Springfield", "query": "Springfield", "constraint_any": [cls("City"), cls("Town"), cls("Village")]},
    {"name": "County seat", "query": "county seat", "constraint_any": [cls("City"), cls("Town")]},
    {"name": "Downtown municipality", "query": "downtown municipality", "constraint_any": [cls("City")]},
    {"name": "Incorporated place", "query": "incorporated place", "constraint_any": [cls("City"), cls("Town"), cls("Village")]},

    {"name": "Town center", "query": "town center", "constraint_any": [cls("Town")]},
    {"name": "Old town", "query": "old town", "constraint_any": [cls("Town")]},
    {"name": "New England town", "query": "New England town", "constraint_any": [cls("Town")]},
    {"name": "Township", "query": "township", "constraint_any": [cls("Town")]},

    {"name": "Small village", "query": "small village", "constraint_any": [cls("Village")]},
    {"name": "Village center", "query": "village center", "constraint_any": [cls("Village")]},
    {"name": "Village in Illinois", "query": "village in Illinois", "constraint_any": [cls("Village")]},
    {"name": "Historic village", "query": "historic village", "constraint_any": [cls("Village")]},

    {"name": "City hall", "query": "city hall", "constraint_any": [cls("Building")]},
    {"name": "Memorial building", "query": "memorial building", "constraint_any": [cls("Building")]},
    {"name": "Downtown tower", "query": "downtown tower", "constraint_any": [cls("Building")]},
    {"name": "County courthouse", "query": "county courthouse", "constraint_any": [cls("Building")]},

    {"name": "First Baptist", "query": "First Baptist", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Saint Mary", "query": "Saint Mary church", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Cathedral downtown", "query": "cathedral downtown", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Temple in California", "query": "temple in California", "constraint_any": [cls("ReligiousBuilding")]},

    {"name": "Lake dam", "query": "lake dam", "constraint_any": [cls("Dam")]},
    {"name": "Power dam", "query": "power dam", "constraint_any": [cls("Dam")]},
    {"name": "River reservoir", "query": "river reservoir", "constraint_any": [cls("Dam")]},

    {"name": "Memorial stadium", "query": "Memorial Stadium", "constraint_any": [cls("Stadium")]},
    {"name": "Home field", "query": "home field", "constraint_any": [cls("Stadium")]},
    {"name": "Civic center", "query": "civic center", "constraint_any": [cls("Venue")]},
    {"name": "Arena downtown", "query": "arena downtown", "constraint_any": [cls("Venue"), cls("Stadium")]},

    {"name": "Public library", "query": "public library", "constraint_any": [cls("Library")]},
    {"name": "Memorial library", "query": "memorial library", "constraint_any": [cls("Library")]},
    {"name": "Medical center", "query": "medical center", "constraint_any": [cls("Hospital")]},
    {"name": "General hospital", "query": "general hospital", "constraint_any": [cls("Hospital")]},

    {"name": "Learning center", "query": "learning center", "constraint_any": [cls("EducationalInstitution")]},
    {"name": "Event center", "query": "event center", "constraint_any": [cls("Venue")]},
    {"name": "Public building", "query": "public building", "constraint_any": [cls("Building"), cls("ArchitecturalStructure")]},
]
