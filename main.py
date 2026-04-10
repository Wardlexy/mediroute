from groq import Groq
import os

# ── Config ──────────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are MediRoute, a healthcare triage assistant that helps users determine 
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
- Always be empathetic and reassuring
"""

# ── Triage parser ────────────────────────────────────────────────────────────
def parse_triage(response: str) -> dict | None:
    if "TRIAGE_RESULT:" not in response:
        return None

    result = {}
    for line in response.split("\n"):
        line = line.strip()
        if line.startswith("- Level:"):
            result["level"] = line.replace("- Level:", "").strip()
        elif line.startswith("- Reason:"):
            result["reason"] = line.replace("- Reason:", "").strip()
        elif line.startswith("- Recommendation:"):
            result["recommendation"] = line.replace("- Recommendation:", "").strip()
        elif line.startswith("- Message:"):
            result["message"] = line.replace("- Message:", "").strip()

    return result if result else None

def display_triage(triage: dict):
    icons = {"MILD": "🟢", "MODERATE": "🟡", "SEVERE": "🔴"}
    level = triage.get("level", "UNKNOWN")
    icon  = icons.get(level, "⚪")

    print("\n" + "=" * 50)
    print(f"  {icon}  TRIAGE RESULT: {level}")
    print("=" * 50)
    print(f"  Reason        : {triage.get('reason', '-')}")
    print(f"  Recommendation: {triage.get('recommendation', '-')}")
    print(f"  Message       : {triage.get('message', '-')}")
    print("=" * 50 + "\n")


# ── Chat loop ────────────────────────────────────────────────────────────────
def chat():
    conversation_history = []
    print("\n🏥 Welcome to MediRoute — Healthcare Triage Assistant")
    print("Type 'quit' or 'exit' to end the session.\n")

    # Initial greeting from agent
    initial_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": "Hello"}
        ]
    )
    greeting = initial_response.choices[0].message.content
    print(f"MediRoute: {greeting}\n")
    conversation_history.append({"role": "assistant", "content": greeting})

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            print("\nMediRoute: Take care! Semoga lekas sembuh 🙏")
            break

        conversation_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history
            ]
        )

        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message})

        # Check if triage result is in response
        triage = parse_triage(assistant_message)
        if triage:
            # Print response without the raw TRIAGE_RESULT block
            clean_response = assistant_message.split("TRIAGE_RESULT:")[0].strip()
            print(f"\nMediRoute: {clean_response}")
            display_triage(triage)
        else:
            print(f"\nMediRoute: {assistant_message}\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    chat()
