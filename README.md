# 🗺 Trip Planner

AI-powered + curated travel itinerary generator. Enter destinations and dates → get a full day-by-day itinerary with activities, food, places, transport, tips, and budget.

**Two modes:**
- 🧠 **AI mode** — calls OpenRouter via backend for personalized itineraries for ANY city
- 📖 **Curated mode** — 15+ cities built-in, generic fallback for everything else (works offline)

## Deploy to Vercel (free)

### 1. Create a GitHub repo

```bash
# From the project root
git init
git add .
git commit -m "Initial commit"
gh repo create trip-planner --public --push
```

Or create one manually at [github.com/new](https://github.com/new) and push.

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import your GitHub repo
3. **Framework Preset**: leave as "Other"
4. **Root Directory**: `/` (the project root)
5. **Environment Variables** → Add:
   - `OPENROUTER_API_KEY` = `sk-or-v1-xxxxxxxxx` (your key)
   - `OPENROUTER_MODEL` = `openrouter/free` (or `deepseek/deepseek-v4-flash`, `nvidia/nemotron-3-ultra-550b-a55b:free`)
6. Click **Deploy**

That's it. Vercel auto-detects the `vercel.json` config.

### 3. Share the URL

Your friends get the same URL. No API key exposed — it stays server-side.

### Optional: Custom domain

In Vercel dashboard → Project → **Domains** → add your domain.

## Project structure

```
trip-planner-web/
├── api/
│   └── index.py         # Flask API (calls OpenRouter)
├── frontend/
│   └── index.html        # Web UI (self-contained)
├── vercel.json           # Vercel deployment config
└── requirements.txt      # Flask dependency
```

## Development

Run locally:
```bash
cd trip-planner-web
pip install -r requirements.txt
OPENROUTER_API_KEY=sk-or-... python api/index.py
# Opens on http://localhost:5000
```

Or serve the frontend alone (no AI, curated only):
```bash
python -m http.server 8080 --directory frontend
```

## Adding cities to the curated database

Open `frontend/index.html` and find the `CURATED` object. Add a new entry:
```js
"Bangkok": {
  activities: "Grand Palace • Wat Pho • Chatuchak Market • Khao San Road • Floating market • Rooftop bar",
  food: "Pad Thai • Tom Yum Goong • Green curry • Mango sticky rice • Street food",
  places: "Grand Palace • Wat Arun • Khao San Road • Siam • Chatuchak",
  accommodation: "Hotel near Sukhumvit or Old City",
  tips: ["Get a Rabbit Card for BTS Skytrain.", "Street food at Yaowarat (Chinatown) is legendary.", "Temples require covered shoulders & knees.", "Bargain at markets — start at 50% of asking price."]
}
```
