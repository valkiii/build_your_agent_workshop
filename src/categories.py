# categories.py — a small library of ready-made sources, grouped by topic, for
# the sidebar's "Categories" one-click-add feature in app.py.
#
# Every homepage + rss pair below was fetched and parsed live (requests +
# feedparser) before being added here, each returning at least 3 real,
# current entries — not guessed. Re-verify before reusing this list somewhere
# with a much later "as of" date; blogs move, get sold, or shut down.

CATEGORIES = {
    "Technology & AI": [
        {"name": "Google Research Blog", "homepage": "https://research.google/blog/", "rss": "https://research.google/blog/rss/"},
        {"name": "DeepMind Blog", "homepage": "https://deepmind.google/discover/blog/", "rss": "https://deepmind.google/discover/blog/feed/"},
        {"name": "Hacker News (front page)", "homepage": "https://news.ycombinator.com/", "rss": "https://news.ycombinator.com/rss"},
        {"name": "Ars Technica", "homepage": "https://arstechnica.com/", "rss": "https://arstechnica.com/feed/"},
        {"name": "The Verge", "homepage": "https://www.theverge.com/", "rss": "https://www.theverge.com/rss/index.xml"},
    ],
    "Science": [
        {"name": "ScienceDaily", "homepage": "https://www.sciencedaily.com/", "rss": "https://www.sciencedaily.com/rss/all.xml"},
        {"name": "Quanta Magazine", "homepage": "https://www.quantamagazine.org/", "rss": "https://www.quantamagazine.org/feed/"},
        {"name": "NASA", "homepage": "https://www.nasa.gov/", "rss": "https://www.nasa.gov/feed/"},
        {"name": "Scientific American", "homepage": "https://www.scientificamerican.com/", "rss": "https://www.scientificamerican.com/platform/syndication/rss/"},
    ],
    "Business & Economics": [
        {"name": "Federal Reserve (monetary policy)", "homepage": "https://www.federalreserve.gov/", "rss": "https://www.federalreserve.gov/feeds/press_monetary.xml"},
        {"name": "NPR Planet Money", "homepage": "https://www.npr.org/sections/money/", "rss": "https://feeds.npr.org/1006/rss.xml"},
        {"name": "Freakonomics", "homepage": "https://freakonomics.com/", "rss": "https://freakonomics.com/feed/"},
        {"name": "Calculated Risk", "homepage": "https://www.calculatedriskblog.com/", "rss": "https://www.calculatedriskblog.com/feeds/posts/default"},
        {"name": "Project Syndicate", "homepage": "https://www.project-syndicate.org/", "rss": "https://www.project-syndicate.org/rss/"},
    ],
    "Health & Wellness": [
        {"name": "Psychology Today", "homepage": "https://www.psychologytoday.com/", "rss": "https://www.psychologytoday.com/us/front/feed"},
        {"name": "NPR Health", "homepage": "https://www.npr.org/sections/health/", "rss": "https://feeds.npr.org/1001/rss.xml"},
        {"name": "Cleveland Clinic Health Essentials", "homepage": "https://health.clevelandclinic.org/", "rss": "https://health.clevelandclinic.org/feed.xml"},
    ],
    "Cooking & Food": [
        {"name": "Recipes from Italy", "homepage": "https://www.recipesfromitaly.com/", "rss": "https://www.recipesfromitaly.com/feed/"},
        {"name": "Smitten Kitchen", "homepage": "https://smittenkitchen.com/", "rss": "https://smittenkitchen.com/feed/"},
        {"name": "Budget Bytes", "homepage": "https://www.budgetbytes.com/", "rss": "https://www.budgetbytes.com/feed/"},
        {"name": "Minimalist Baker", "homepage": "https://minimalistbaker.com/", "rss": "https://minimalistbaker.com/feed/"},
        {"name": "The Pasta Project", "homepage": "https://www.the-pasta-project.com/", "rss": "https://www.the-pasta-project.com/feed/"},
    ],
    "Personal Finance": [
        {"name": "Mr. Money Mustache", "homepage": "https://www.mrmoneymustache.com/", "rss": "https://www.mrmoneymustache.com/feed/"},
        {"name": "Get Rich Slowly", "homepage": "https://www.getrichslowly.org/", "rss": "https://www.getrichslowly.org/feed/"},
        {"name": "Financial Samurai", "homepage": "https://www.financialsamurai.com/", "rss": "https://www.financialsamurai.com/feed/"},
        {"name": "Afford Anything", "homepage": "https://affordanything.com/", "rss": "https://affordanything.com/feed/"},
    ],
    "Design & UX": [
        {"name": "Smashing Magazine", "homepage": "https://www.smashingmagazine.com/", "rss": "https://www.smashingmagazine.com/feed/"},
        {"name": "A List Apart", "homepage": "https://alistapart.com/", "rss": "https://alistapart.com/main/feed/"},
        {"name": "CSS-Tricks", "homepage": "https://css-tricks.com/", "rss": "https://css-tricks.com/feed/"},
    ],
    "Climate & Environment": [
        {"name": "Yale Environment 360", "homepage": "https://e360.yale.edu/", "rss": "https://e360.yale.edu/feed.xml"},
        {"name": "Grist", "homepage": "https://grist.org/", "rss": "https://grist.org/feed/"},
        {"name": "The Guardian (Environment)", "homepage": "https://www.theguardian.com/environment", "rss": "https://www.theguardian.com/uk/environment/rss"},
    ],
    "Sports": [
        {"name": "BBC Sport", "homepage": "https://www.bbc.com/sport", "rss": "https://feeds.bbci.co.uk/sport/rss.xml"},
        {"name": "The Guardian (Sport)", "homepage": "https://www.theguardian.com/sport", "rss": "https://www.theguardian.com/uk/sport/rss"},
        {"name": "ESPN (top headlines)", "homepage": "https://www.espn.com/", "rss": "https://www.espn.com/espn/rss/news"},
        {"name": "SB Nation", "homepage": "https://www.sbnation.com/", "rss": "https://www.sbnation.com/rss/index.xml"},
    ],
    "Travel": [
        {"name": "Nomadic Matt", "homepage": "https://www.nomadicmatt.com/", "rss": "https://www.nomadicmatt.com/feed/"},
        {"name": "The Points Guy", "homepage": "https://thepointsguy.com/", "rss": "https://thepointsguy.com/feed/"},
        {"name": "Legal Nomads", "homepage": "https://www.legalnomads.com/", "rss": "https://www.legalnomads.com/feed/"},
        {"name": "Atlas Obscura", "homepage": "https://www.atlasobscura.com/", "rss": "https://www.atlasobscura.com/feeds/latest"},
    ],
}
