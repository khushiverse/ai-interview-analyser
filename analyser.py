import nltk
import re
import requests
import time
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------- HUGGING FACE API ----------------
def get_hf_api_key():
    return os.getenv("HF_API_KEY", "").strip()

def _call_hf_chat(messages, max_tokens=250, temperature=0.4):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    MODEL_ID = "katanemo/Arch-Router-1.5B:hf-inference"
    hf_api_key = get_hf_api_key()

    if not hf_api_key:
        return None, "Missing HF_API_KEY environment variable."

    headers = {
        "Authorization": f"Bearer {hf_api_key}",
        "Content-Type": "application/json",
    }

    for _ in range(3):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "model": MODEL_ID,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=20,
            )
        except requests.RequestException as exc:
            return None, f"AI request failed: {exc}"

        if response.status_code == 200:
            try:
                data = response.json()
                if (
                    isinstance(data, dict)
                    and "choices" in data
                    and data["choices"]
                    and "message" in data["choices"][0]
                    and "content" in data["choices"][0]["message"]
                ):
                    return data["choices"][0]["message"]["content"].strip(), None
                return None, "AI returned unexpected format."
            except (ValueError, KeyError, IndexError, TypeError):
                return None, "AI returned unexpected format."

        elif response.status_code == 503:
            time.sleep(5)

        else:
            return None, f"Error {response.status_code}: {response.text}"

    return None, "Model is loading. Try again."


def rewrite_answer_hf(answer, question):
    messages = [
        {
            "role": "system",
            "content": "You are an interview coach. Rewrite answers so they are clear, confident, concise, and well-structured.",
        },
        {
            "role": "user",
            "content": (
                f'Question: "{question}"\n\n'
                f'Original answer:\n{answer}\n\n'
                "Rewrite it as a strong interview answer in first person."
            ),
        },
    ]
    return _call_hf_chat(messages, max_tokens=250, temperature=0.4)


# ---------------- BASIC FALLBACK REWRITE ----------------
def rewrite_answer_basic(answer):
    sentences = answer.split('.')
    
    improved = []
    for s in sentences:
        s = s.strip()
        if s:
            improved.append(s.capitalize())

    return ". ".join(improved) + "."


def rewrite_answer(answer, question):
    improved, error = rewrite_answer_hf(answer, question)

    if not improved:
        return rewrite_answer_basic(answer), "basic", error or "Empty AI response."

    return improved, "ai", None


def generate_ai_feedback(answer, question, fillers, sentiment, structure, matched_keywords, missing_keywords):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert interview coach. Give practical, concise feedback in Markdown. "
                "Be specific, encouraging but direct, and tailored to the candidate's answer."
            ),
        },
        {
            "role": "user",
            "content": (
                f'Interview question: "{question}"\n\n'
                f"Candidate answer:\n{answer}\n\n"
                f"Analysis signals:\n"
                f"- filler words: {fillers}\n"
                f"- sentiment score: {sentiment}\n"
                f"- structure: {structure}\n"
                f"- matched keywords: {', '.join(matched_keywords) if matched_keywords else 'none'}\n"
                f"- missing keywords: {', '.join(missing_keywords) if missing_keywords else 'none'}\n\n"
                "Respond in this exact structure:\n"
                "### What Works\n"
                "2-3 short bullet points.\n\n"
                "### What To Improve\n"
                "2-3 short bullet points.\n\n"
                "### Better Answer\n"
                "One polished interview answer in first person, 90-140 words."
            ),
        },
    ]
    return _call_hf_chat(messages, max_tokens=420, temperature=0.5)


# ---------------- SENTIMENT SETUP ----------------
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
except:
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()


# ---------------- FILLER WORD DETECTION ----------------
def detect_filler_words(text):
    fillers = ["um", "uh", "like", "you know", "basically", "so", "actually"]
    
    words = re.findall(r'\b\w+\b', text.lower())
    count = sum(word in fillers for word in words)
    
    return count


# ---------------- SENTIMENT ----------------
def analyze_sentiment(text):
    score = sia.polarity_scores(text)
    return score['compound']


# ---------------- STRUCTURE ----------------
def evaluate_structure(text):
    length = len(text.split())

    if length < 30:
        return "Too short"
    elif length > 150:
        return "Too long"
    else:
        return "Good length"


# ---------------- SCORING ----------------
def generate_score(filler_count, sentiment):
    score = 10

    score -= filler_count * 0.5

    if sentiment < 0:
        score -= 2

    return max(round(score, 1), 1)


# ---------------- KEYWORD MATCHING ----------------
def keyword_match(answer, expected_keywords):
    words = re.findall(r'\b\w+\b', answer.lower())

    matched = []
    for keyword in expected_keywords:
        if keyword in words:
            matched.append(keyword)

    missing = [k for k in expected_keywords if k not in matched]

    return matched, missing


# ---------------- SMART FEEDBACK ----------------
def generate_smart_feedback(fillers, sentiment, structure, missing_keywords):
    feedback = []

    if fillers > 3:
        feedback.append("Reduce filler words to sound more confident.")

    if sentiment < 0:
        feedback.append("Use more positive and assertive language.")

    if structure == "Too short":
        feedback.append("Expand your answer with more details and examples.")
    elif structure == "Too long":
        feedback.append("Keep your answer concise and to the point.")
    else:
        feedback.append("Your answer length is appropriate.")

    if len(missing_keywords) > 2:
        feedback.append("Include more relevant points to improve your answer.")

    if not feedback:
        feedback.append("Good job! Your answer is strong.")

    return feedback
