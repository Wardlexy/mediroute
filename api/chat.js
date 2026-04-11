export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { messages, action, lat, lng, triageLevel } = req.body;

  const GROQ_API_KEY        = process.env.GROQ_API_KEY;
  const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

  // ── Action: find nearby facilities ──────────────────────────────────────
  if (action === "find_facilities") {
    if (!GOOGLE_MAPS_API_KEY) return res.status(500).json({ error: "Maps API key not configured" });
    if (!lat || !lng)         return res.status(400).json({ error: "Location required" });

    const keywords = {
      MILD:     "apotek farmasi",
      MODERATE: "puskesmas klinik",
      SEVERE:   "rumah sakit IGD"
    };

    const level   = triageLevel || "MODERATE";
    const keyword = keywords[level] || keywords.MODERATE;
    const radius  = level === "SEVERE" ? 5000 : 3000;

    const url = `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${lat},${lng}&radius=${radius}&keyword=${encodeURIComponent(keyword)}&language=id&key=${GOOGLE_MAPS_API_KEY}`;

    const response = await fetch(url);
    const data     = await response.json();

    if (data.status !== "OK" && data.status !== "ZERO_RESULTS") {
      return res.status(500).json({ error: `Maps API error: ${data.status}` });
    }

    const facilities = (data.results || []).slice(0, 3).map(place => ({
      name:    place.name,
      address: place.vicinity,
      rating:  place.rating || null,
      open:    place.opening_hours?.open_now ?? null,
      lat:     place.geometry.location.lat,
      lng:     place.geometry.location.lng,
      mapsUrl: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}&query_place_id=${place.place_id}`
    }));

    return res.status(200).json({ facilities });
  }

  // ── Action: chat ─────────────────────────────────────────────────────────
  if (!messages) return res.status(400).json({ error: "Messages required" });
  if (!GROQ_API_KEY) return res.status(500).json({ error: "API key not configured" });

  const SYSTEM_PROMPT = `You are MediRoute, a healthcare triage assistant that helps users determine 
the urgency of their symptoms and recommend the appropriate healthcare facility.

## LANGUAGE
- Detect the user's language automatically and respond in the same language
- If user writes in Bahasa Indonesia → respond in Bahasa Indonesia
- If user writes in English → respond in English
- Maintain the same language throughout the conversation
- Use friendly, casual but professional tone
- Avoid overly technical medical jargon

## CONVERSATION FLOW
1. Greet the user and ask them to describe their symptoms
2. Ask follow-up questions ONE AT A TIME (max 4 questions total):
   - Pain/discomfort severity (scale 1-10)
   - Duration of symptoms
   - Accompanying symptoms (fever, vomiting, difficulty breathing, etc.)
   - Previous medication taken
3. After gathering enough info, give triage assessment
4. Recommend appropriate facility

## TRIAGE LEVELS
🟢 MILD - Symptoms are mild, no immediate danger
→ Recommend: Rest at home, pharmacy (apotek)

🟡 MODERATE - Symptoms need medical attention but not emergency
→ Recommend: Puskesmas or klinik umum

🔴 SEVERE - Symptoms are severe or potentially dangerous
→ Recommend: Rumah Sakit or IGD immediately

## TRIAGE OUTPUT FORMAT
After assessment, always output in this exact format:

TRIAGE_RESULT:
- Level: [MILD/MODERATE/SEVERE]
- Reason: [brief explanation in English]
- Recommendation: [type of facility in English]
- Message: [caring closing message in English]

## IMPORTANT RULES
- You are NOT a doctor, always add disclaimer
- For SEVERE cases, urge user to seek help immediately
- Never diagnose specific diseases, only assess urgency
- If user mentions chest pain, difficulty breathing, or stroke symptoms → immediately classify as SEVERE
- Always be empathetic and reassuring`;

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        temperature: 0.7,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages
        ]
      })
    });

    const data  = await response.json();
    const reply = data.choices[0].message.content;
    res.status(200).json({ reply });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to fetch from Groq" });
  }
}
