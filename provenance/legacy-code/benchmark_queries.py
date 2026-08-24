TESTS = [
    {
        "name": "Waypoints near JFK",
        "query": "navigation waypoint near JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Arrival fixes for JFK",
        "query": "arrival fixes for JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Route segments near JFK",
        "query": "arrival route segment near JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Route leg on J37",
        "query": "route leg on J37",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Current weather at JFK",
        "query": "current weather at JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Surface observation for KEWR",
        "query": "surface observation for KEWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Forecast weather for EWR",
        "query": "forecast weather for EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Terminal forecast for KJFK",
        "query": "terminal forecast for KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Airport code NY94",
        "query": "airport code NY94",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Airport in America New York timezone",
        "query": "airport in America New York timezone",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Waypoint fix near Newark",
        "query": "navigation waypoint near Newark",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Waypoint fix near LaGuardia",
        "query": "navigation waypoint near LaGuardia",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Fixes used for arrivals into EWR",
        "query": "arrival fixes for EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Fixes used for arrivals into LGA",
        "query": "arrival fixes for LGA",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Fixes for departures from JFK",
        "query": "departure fixes for JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Fixes for departures from EWR",
        "query": "departure fixes for EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Intersection fix around JFK",
        "query": "intersection fix around JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Lat lon fix near New York airport",
        "query": "lat lon fix near New York airport",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Navigation fix near KJFK",
        "query": "navigation fix near KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Waypoint in New York terminal area",
        "query": "waypoint in New York terminal area",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Route segment near Newark",
        "query": "arrival route segment near Newark",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Route segment near LaGuardia",
        "query": "arrival route segment near LaGuardia",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Departure route segment from JFK",
        "query": "departure route segment from JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Departure route segment from EWR",
        "query": "departure route segment from EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Jet route leg on J75",
        "query": "route leg on J75",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Jet route leg on J80",
        "query": "route leg on J80",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Jet route segment in New York region",
        "query": "jet route segment in New York region",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Airway segment near JFK",
        "query": "airway segment near JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Segment of arrival route into KJFK",
        "query": "segment of arrival route into KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Segment of route near EWR",
        "query": "segment of route near EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "METAR for KJFK",
        "query": "METAR for KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "METAR for Newark airport",
        "query": "METAR for Newark airport",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Surface weather report for JFK",
        "query": "surface weather report for JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Observed weather at LaGuardia",
        "query": "observed weather at LaGuardia",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Latest METAR at KEWR",
        "query": "latest METAR at KEWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Current surface observation at JFK",
        "query": "current surface observation at JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Weather observation for KJFK",
        "query": "weather observation for KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Airport weather report for EWR",
        "query": "airport weather report for EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "TAF for KEWR",
        "query": "TAF for KEWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "TAF for KLGA",
        "query": "TAF for KLGA",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Terminal forecast for Newark",
        "query": "terminal forecast for Newark",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Terminal forecast for LaGuardia",
        "query": "terminal forecast for LaGuardia",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Forecast weather for JFK airport",
        "query": "forecast weather for JFK airport",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Airport forecast for KEWR",
        "query": "airport forecast for KEWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Aviation forecast for KJFK",
        "query": "aviation forecast for KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Future weather at Newark airport",
        "query": "future weather at Newark airport",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Airport code for JFK",
        "query": "airport code for JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Airport code for Newark",
        "query": "airport code for Newark",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Airport in America Chicago timezone",
        "query": "airport in America Chicago timezone",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Airport in Eastern timezone",
        "query": "airport in eastern timezone",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
]
