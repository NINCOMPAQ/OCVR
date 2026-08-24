DBO = "http://dbpedia.org/ontology/"


def cls(name: str) -> str:
    return f"{DBO}{name}"


TESTS = [
    {"name": "After high school", "query": "where students go after high school", "constraint_any": [cls("University")]},
    {"name": "Four year campus", "query": "four year campus with dorms", "constraint_any": [cls("University")]},
    {"name": "Research campus", "query": "research campus with graduate programs", "constraint_any": [cls("University")]},
    {"name": "State campus", "query": "state campus in California", "constraint_any": [cls("University")]},

    {"name": "Kids weekday place", "query": "where children go on weekday mornings", "constraint_any": [cls("School")]},
    {"name": "Teenagers classes", "query": "place where teenagers take classes", "constraint_any": [cls("School")]},
    {"name": "Local academy", "query": "local academy for students", "constraint_any": [cls("School")]},
    {"name": "Public classroom place", "query": "public classroom place in a neighborhood", "constraint_any": [cls("School")]},

    {"name": "Big municipality", "query": "big municipality with a downtown", "constraint_any": [cls("City")]},
    {"name": "Mayor and downtown", "query": "place with a mayor and downtown", "constraint_any": [cls("City")]},
    {"name": "Urban center", "query": "urban center with neighborhoods", "constraint_any": [cls("City")]},
    {"name": "Large incorporated place", "query": "large incorporated place in a state", "constraint_any": [cls("City")]},

    {"name": "Smaller municipality", "query": "smaller municipality outside a city", "constraint_any": [cls("Town")]},
    {"name": "Main street place", "query": "place with a main street and town hall", "constraint_any": [cls("Town")]},
    {"name": "New England local government", "query": "New England local government place", "constraint_any": [cls("Town")]},
    {"name": "Small incorporated community", "query": "small incorporated community", "constraint_any": [cls("Town"), cls("Village")]},

    {"name": "Tiny incorporated community", "query": "tiny incorporated community", "constraint_any": [cls("Village")]},
    {"name": "Small rural place", "query": "small rural place with local government", "constraint_any": [cls("Village")]},
    {"name": "Not quite a town", "query": "not quite a town but officially named", "constraint_any": [cls("Village")]},
    {"name": "Little settlement", "query": "little settlement in Illinois", "constraint_any": [cls("Village")]},

    {"name": "Government offices", "query": "place with government offices downtown", "constraint_any": [cls("Building")]},
    {"name": "Tall downtown place", "query": "tall downtown place with an architect", "constraint_any": [cls("Building")]},
    {"name": "Old courthouse", "query": "old courthouse near the county seat", "constraint_any": [cls("Building")]},
    {"name": "Named public structure", "query": "named public structure in a city", "constraint_any": [cls("Building")]},

    {"name": "Sunday morning place", "query": "where people gather on Sunday morning", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Old stone church", "query": "old stone church", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Worship services", "query": "place used for worship services", "constraint_any": [cls("ReligiousBuilding")]},
    {"name": "Saint building", "query": "Saint Mary building", "constraint_any": [cls("ReligiousBuilding")]},

    {"name": "Holds back water", "query": "structure that holds back water", "constraint_any": [cls("Dam")]},
    {"name": "Makes a reservoir", "query": "thing that makes a reservoir", "constraint_any": [cls("Dam")]},
    {"name": "River power structure", "query": "river power structure", "constraint_any": [cls("Dam")]},

    {"name": "Friday night game", "query": "place for a Friday night game", "constraint_any": [cls("Stadium")]},
    {"name": "Home field seats", "query": "home field with seats", "constraint_any": [cls("Stadium")]},
    {"name": "Large game venue", "query": "large place for games and fans", "constraint_any": [cls("Stadium"), cls("Venue")]},
    {"name": "Concert and game place", "query": "place for concerts and games", "constraint_any": [cls("Venue")]},

    {"name": "Borrow books", "query": "place where people borrow books", "constraint_any": [cls("Library")]},
    {"name": "Reading rooms", "query": "building with reading rooms and collections", "constraint_any": [cls("Library")]},
    {"name": "Emergency care", "query": "place to get emergency care", "constraint_any": [cls("Hospital")]},
    {"name": "Patients and doctors", "query": "place with patients and doctors", "constraint_any": [cls("Hospital")]},

    {"name": "Learning place broad", "query": "place for learning and research", "constraint_any": [cls("EducationalInstitution")]},
    {"name": "Public events broad", "query": "place for public events", "constraint_any": [cls("Venue")]},
    {"name": "Human-made place broad", "query": "human made place you can enter", "constraint_any": [cls("Building"), cls("ArchitecturalStructure")]},
]
