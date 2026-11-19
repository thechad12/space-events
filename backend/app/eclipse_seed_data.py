"""
Seed data for the `eclipses` table (NASA-verified, 2024-2028).

The app reads eclipses from Postgres at runtime. To add or edit eclipses, either
edit rows in the database directly, or edit this list and re-run:

    cd backend && python -m app.seed_eclipses
"""

ECLIPSE_CATALOG = [
    # 2024
    {
        "type": "solar_eclipse", "date": "2024-04-08", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 268,
        "path_description": "Path of totality crosses Mexico, central USA (Texas to Maine), and eastern Canada.",
        "visibility_regions": ["north_america"],
        "description": "A spectacular total solar eclipse crosses North America. Totality lasts up to 4m 28s in the path.",
    },
    {
        "type": "lunar_eclipse", "date": "2024-09-17", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse", "duration_min": 62,
        "path_description": "Visible from Europe, Africa, Americas.",
        "visibility_regions": ["europe", "africa", "americas"],
        "description": "The Moon passes through part of Earth's umbral shadow. About 8% of the Moon is covered at maximum.",
    },
    {
        "type": "solar_eclipse", "date": "2024-10-02", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Annular path crosses southern Chile and Argentina.",
        "visibility_regions": ["south_america"],
        "description": "A ring of fire eclipse visible along a narrow path through South America.",
    },
    # 2025
    {
        "type": "lunar_eclipse", "date": "2025-03-13", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 65,
        "path_description": "Visible from Americas, Europe, Africa, western Asia.",
        "visibility_regions": ["americas", "europe", "africa"],
        "description": "A vivid Blood Moon eclipse visible across the Americas and Europe. Total phase lasts about 65 minutes.",
    },
    {
        "type": "solar_eclipse", "date": "2025-03-29", "eclipse_type": "partial",
        "name": "Partial Solar Eclipse",
        "path_description": "Visible from NW Africa, Europe, northern Asia.",
        "visibility_regions": ["europe", "africa"],
        "description": "A partial solar eclipse visible across Europe, northwestern Africa, and parts of northern Asia.",
    },
    {
        "type": "lunar_eclipse", "date": "2025-09-07", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 82,
        "path_description": "Visible from Europe, Africa, Asia, Australia.",
        "visibility_regions": ["europe", "africa", "asia", "australia"],
        "description": "A deep total lunar eclipse visible across Europe, Africa, Asia, and Australia. Total phase lasts 82 minutes.",
    },
    {
        "type": "solar_eclipse", "date": "2025-09-21", "eclipse_type": "partial",
        "name": "Partial Solar Eclipse",
        "path_description": "Visible from southern Australia, New Zealand, Antarctica.",
        "visibility_regions": ["australia"],
        "description": "A partial solar eclipse across the southern Pacific and Antarctica region.",
    },
    # 2026
    {
        "type": "lunar_eclipse", "date": "2026-03-03", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 58,
        "path_description": "Visible from Americas, Europe, Africa, western Pacific.",
        "visibility_regions": ["americas", "europe", "africa"],
        "description": "Total lunar eclipse with 58-minute totality visible across the Americas and Europe.",
    },
    {
        "type": "solar_eclipse", "date": "2026-02-17", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Annular path crosses Antarctica and the southern tips of South America.",
        "visibility_regions": ["south_america"],
        "description": "An annular solar eclipse whose path crosses the Antarctic continent.",
    },
    {
        "type": "lunar_eclipse", "date": "2026-08-28", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse",
        "path_description": "Visible from Europe, Africa, Asia, Australia.",
        "visibility_regions": ["europe", "africa", "asia"],
        "description": "A partial lunar eclipse visible from Europe, Africa, and Asia.",
    },
    {
        "type": "solar_eclipse", "date": "2026-08-12", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 145,
        "path_description": "Path of totality crosses Greenland, Iceland, Spain, and Russia.",
        "visibility_regions": ["europe"],
        "description": "A highly anticipated total solar eclipse whose path of totality crosses Greenland, Iceland, and northern Spain.",
    },
    # 2027
    {
        "type": "solar_eclipse", "date": "2027-02-06", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Path crosses southern Atlantic, Africa, Indian Ocean.",
        "visibility_regions": ["africa"],
        "description": "An annular eclipse crossing southern South America, the southern Atlantic, and southern Africa.",
    },
    {
        "type": "solar_eclipse", "date": "2027-08-02", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 396,
        "path_description": "Longest totality of the 21st century. Path crosses North Africa, Middle East, and South Asia.",
        "visibility_regions": ["africa", "asia"],
        "description": "The longest total solar eclipse of the 21st century with up to 6 minutes 23 seconds of totality. Path crosses Morocco, Spain, Algeria, Libya, Egypt, Saudi Arabia, Yemen, and Somalia.",
    },
    {
        "type": "lunar_eclipse", "date": "2027-08-17", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse",
        "path_description": "Visible from most of the world.",
        "visibility_regions": ["americas", "europe", "africa", "asia"],
        "description": "A partial lunar eclipse visible from most of the globe.",
    },
    # 2028
    {
        "type": "lunar_eclipse", "date": "2028-01-12", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 67,
        "path_description": "Visible from Americas, Europe, Africa, Asia.",
        "visibility_regions": ["americas", "europe", "africa", "asia"],
        "description": "A total lunar eclipse with 67-minute totality visible across Americas, Europe, Africa, and much of Asia.",
    },
    {
        "type": "solar_eclipse", "date": "2028-01-26", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Path crosses Ecuador, Peru, Brazil, southern Atlantic, and southern Africa.",
        "visibility_regions": ["south_america", "africa"],
        "description": "An annular solar eclipse whose path crosses South America and southern Africa.",
    },
    {
        "type": "solar_eclipse", "date": "2028-07-22", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 309,
        "path_description": "Path crosses Australia and New Zealand.",
        "visibility_regions": ["australia"],
        "description": "A total solar eclipse bringing up to 5 minutes 10 seconds of totality to parts of Australia and New Zealand.",
    },
]
