SUMMARY_PROMPT = """You are HealthBot, an AI patient education assistant.
Use ONLY the provided web search results text. Do not use other knowledge.

Write a patient-friendly explanation (avoid jargon, define medical terms simply).
Produce 3–4 short paragraphs, then a "Key takeaways" section with 4–6 bullets.

You MUST include inline citations like [SRC1], [SRC2] that refer to the Sources list.

Add a short disclaimer: "Educational information only — not medical advice."

SOURCES:
{sources}

WEB RESULTS TEXT:
{results_text}
"""

QUIZ_PROMPT = """Create exactly ONE comprehension-check question based ONLY on the summary below.
The question must be answerable using the summary alone and be patient-friendly.

Return JSON only with keys:
question, expected_answer

SUMMARY:
{summary}
"""

GRADE_PROMPT = """Grade the patient's answer using ONLY the summary below.

Return JSON only with keys:
grade, explanation, citations

Rules:
- grade must be one of: A, B, C, D, F
- explanation: 3–6 sentences, patient-friendly
- citations: include 1–3 short verbatim quote snippets from the summary that support your explanation.
  Keep the citation tags like [SRC1] exactly as in the summary.

SUMMARY:
{summary}

QUESTION:
{question}

PATIENT ANSWER:
{patient_answer}
"""