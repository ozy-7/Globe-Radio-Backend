from rapidfuzz import fuzz

def search_stations(query, stations, limit=100):
    query_lower = query.lower()
    results = []

    max_clickcount = max((s.get('clickcount', 0) for s in stations), default=1)

    for station in stations:
        name = station.get('name', '').lower()
        clickcount = station.get('clickcount', 0)

        fuzzy_score = fuzz.WRatio(query_lower, name)

        if query_lower == name:
            fuzzy_score = 1000  # Exact match highest priority
        elif name.startswith(query_lower):
            fuzzy_score += 100
        elif query_lower in name:
            fuzzy_score += 50

        popularity_score = (clickcount / max_clickcount) * 100

        final_score = fuzzy_score * 0.7 + popularity_score * 0.3

        results.append((station, final_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [station for station, _ in results[:limit]]
