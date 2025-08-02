import json
from rapidfuzz import fuzz

# stations verisi dışarıdan verilecek, max_clickcount her aramada hesaplanıyor
def combined_text(station):
    city = station.get("city", "")
    return f"{station.get('name', '')} {station.get('tags', '')} {station.get('country', '')} {city}".lower()

def extract_location_keywords(query, stations):
    query_words = query.lower().split()
    locations = set()
    for kw in query_words:
        for s in stations:
            city = s.get("city", "").lower()
            country = s.get("country", "").lower()
            if kw == city or kw == country:
                locations.add(kw)
    return locations

def search_stations(query, stations, min_results=10, limit=20):
    query_lc = query.lower()
    keywords = query_lc.split()
    location_keywords = extract_location_keywords(query, stations)
    max_clickcount = max((s.get("clickcount", 0) for s in stations), default=1)

    def matches_all_keywords_loc(station):
        text = combined_text(station)
        return all(k in text for k in keywords)

    results = []
    for s in stations:
        if matches_all_keywords_loc(s):
            name = s.get("name", "").lower()
            exact_match = (name == query_lc)
            name_contains_query = query_lc in name or name in query_lc
            similarity = fuzz.token_sort_ratio(query_lc, name) / 100.0
            popularity = s.get("clickcount", 0) / max_clickcount

            if exact_match:
                score = 1.0 + popularity + 1.0
            elif name_contains_query and similarity > 0.8:
                score = 1.0 + similarity + popularity
            elif similarity > 0.9:
                score = 1.0 + popularity
            else:
                score = similarity * 0.7 + popularity * 0.3

            results.append((score, s))

    results.sort(key=lambda x: x[0], reverse=True)

    # fallback without location keywords if results too few
    if location_keywords and len(results) < min_results:
        filtered_keywords = [k for k in keywords if k not in location_keywords]

        def matches_all_keywords_noloc(station):
            text = combined_text(station)
            return all(k in text for k in filtered_keywords)

        fallback_results = []
        for s in stations:
            if matches_all_keywords_noloc(s):
                name = s.get("name", "").lower()
                exact_match = (name == query_lc)
                name_contains_query = query_lc in name or name in query_lc
                similarity = fuzz.token_sort_ratio(query_lc, name) / 100.0
                popularity = s.get("clickcount", 0) / max_clickcount

                if exact_match:
                    score = 1.0 + popularity + 1.0
                elif name_contains_query and similarity > 0.8:
                    score = 1.0 + similarity + popularity
                elif similarity > 0.9:
                    score = 1.0 + popularity
                else:
                    score = similarity * 0.7 + popularity * 0.3

                fallback_results.append((score, s))

        fallback_results.sort(key=lambda x: x[0], reverse=True)
        existing = set(id(s[1]) for s in results)
        for item in fallback_results:
            if id(item[1]) not in existing:
                results.append(item)
                existing.add(id(item[1]))
                if len(results) >= min_results:
                    break

        results.sort(key=lambda x: x[0], reverse=True)

    # supplement with popular stations if still too few
    if len(results) < 5:
        popular_candidates = []
        for s in stations:
            name = s.get("name", "").lower()
            similarity = fuzz.token_sort_ratio(query_lc, name) / 100.0
            popularity = s.get("clickcount", 0) / max_clickcount
            score = similarity * 0.5 + popularity * 0.5
            popular_candidates.append((score, s))

        popular_candidates.sort(key=lambda x: x[0], reverse=True)
        existing = set(id(s[1]) for s in results)
        for item in popular_candidates:
            if id(item[1]) not in existing:
                results.append(item)
                existing.add(id(item[1]))
                if len(results) >= min_results:
                    break

        results.sort(key=lambda x: x[0], reverse=True)

    return [s for _, s in results[:limit]]
