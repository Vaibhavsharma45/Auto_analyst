"""
NLP Engine — Sentiment Analysis, Text Stats, Keywords, Readability
No heavy dependencies — uses built-in Python + basic libs
"""
import re
import math
from collections import Counter

# ── Sentiment word lists ──────────────────────────────
POSITIVE_WORDS = {
    'good','great','excellent','amazing','awesome','fantastic','wonderful',
    'positive','best','love','happy','joy','success','profit','growth',
    'increase','improve','better','superior','outstanding','perfect',
    'brilliant','superb','magnificent','exceptional','effective','efficient',
    'strong','powerful','innovative','reliable','quality','valuable',
    'win','gains','revenue','achieve','accomplish','benefit','advantage',
    'recommend','satisfied','impressed','pleased','delighted','helpful'
}
NEGATIVE_WORDS = {
    'bad','terrible','awful','horrible','poor','negative','worst','hate',
    'sad','loss','decline','decrease','fail','failure','problem','issue',
    'error','wrong','broken','damage','risk','danger','concern','worry',
    'difficult','hard','slow','weak','inferior','disappointing','frustrating',
    'useless','waste','expensive','costly','complaint','dissatisfied','unhappy',
    'delay','cancel','reject','refuse','impossible','critical','urgent','severe'
}

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return text.split()

def analyze_sentiment(text):
    words = clean_text(text)
    if not words:
        return {"label": "Neutral", "score": 0.0, "positive": 0, "negative": 0, "total_words": 0}
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = len(words)
    score = (pos - neg) / max(total, 1)
    if score > 0.02:   label = "Positive"
    elif score < -0.02: label = "Negative"
    else:               label = "Neutral"
    return {
        "label": label,
        "score": round(score, 4),
        "positive_words": pos,
        "negative_words": neg,
        "total_words": total,
        "confidence": round(min(abs(score) * 10, 1.0), 2)
    }

def get_keywords(text, top_n=20):
    STOPWORDS = {'the','a','an','and','or','but','in','on','at','to','for',
                 'of','with','by','from','is','are','was','were','be','been',
                 'have','has','had','do','does','did','will','would','could',
                 'should','may','might','this','that','these','those','it',
                 'its','we','they','their','our','your','my','his','her',
                 'not','no','so','if','as','up','out','about','which','who'}
    words = clean_text(text)
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    freq = Counter(filtered)
    total = sum(freq.values())
    result = []
    for word, count in freq.most_common(top_n):
        result.append({
            "word": word,
            "count": count,
            "frequency": round(count/total*100, 2)
        })
    return result

def text_statistics(text):
    text = str(text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()
    chars = len(text.replace(' ',''))
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
    avg_sent_len = len(words) / max(len(sentences), 1)
    # Flesch Reading Ease approximation
    syllables = sum(max(1, len(re.findall(r'[aeiou]', w.lower()))) for w in words)
    if len(words) > 0 and len(sentences) > 0:
        flesch = 206.835 - 1.015*(len(words)/len(sentences)) - 84.6*(syllables/max(len(words),1))
        flesch = max(0, min(100, flesch))
    else:
        flesch = 0
    if flesch >= 80:   readability = "Very Easy"
    elif flesch >= 60: readability = "Easy"
    elif flesch >= 40: readability = "Moderate"
    else:              readability = "Complex"
    return {
        "total_words": len(words),
        "unique_words": len(set(w.lower() for w in words)),
        "total_sentences": len(sentences),
        "total_characters": chars,
        "avg_word_length": round(avg_word_len, 1),
        "avg_sentence_length": round(avg_sent_len, 1),
        "vocabulary_richness": round(len(set(words))/max(len(words),1)*100, 1),
        "readability_score": round(flesch, 1),
        "readability_label": readability
    }

def analyze_column(series):
    """Full NLP analysis on a pandas Series of text"""
    import pandas as pd
    texts = series.dropna().astype(str)
    if len(texts) == 0:
        return {"error": "No text data found"}
    
    # Combine all text for corpus analysis
    corpus = ' '.join(texts.tolist())
    
    # Per-row sentiment
    sentiments = texts.apply(analyze_sentiment)
    labels = [s['label'] for s in sentiments]
    label_counts = Counter(labels)
    avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
    
    return {
        "total_texts": len(texts),
        "sentiment_distribution": dict(label_counts),
        "avg_sentiment_score": round(avg_score, 4),
        "overall_sentiment": "Positive" if avg_score > 0.02 else ("Negative" if avg_score < -0.02 else "Neutral"),
        "keywords": get_keywords(corpus, 25),
        "text_stats": text_statistics(corpus),
        "sample_sentiments": [
            {"text": str(texts.iloc[i])[:100], **sentiments.iloc[i]}
            for i in range(min(5, len(texts)))
        ]
    }