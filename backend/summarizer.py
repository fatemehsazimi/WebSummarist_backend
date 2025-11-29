# backend/summarizer.py
import logging
from typing import Dict, List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_NAME = "facebook/bart-large-cnn"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)
except Exception as e:
    logger.exception("Failed to load model/tokenizer")
    tokenizer = None
    model = None


def _chunk_text_by_words(text: str, chunk_size_words: int = 800) -> List[str]:
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i:i + chunk_size_words]) for i in range(0, len(words), chunk_size_words)]


def _summarize_chunk(chunk: str, device: str = DEVICE) -> str:
    if tokenizer is None or model is None:
        raise RuntimeError("Model or tokenizer not loaded.")

    inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(device)
    
    summary_ids = model.generate(
        inputs["input_ids"],
        attention_mask=inputs.get("attention_mask", None),
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return summary.strip()


def summarize_text(text: str) -> Dict[str, object]:
    if not isinstance(text, str):
        return {"success": False, "error": "Input text must be a string."}

    text = text.strip()
    if not text:
        return {"success": False, "error": "Input text is empty."}

    if tokenizer is None or model is None:
        return {"success": False, "error": "Model or tokenizer is not loaded on server."}

    try:
        words = text.split()
        if len(words) <= 250:
            summary = _summarize_chunk(text)
            if not summary:
                logger.warning("Summary is empty for short text")
                return {"success": False, "error": "Summary is empty."}
            return {"success": True, "summary_text": summary}

        chunks = _chunk_text_by_words(text, chunk_size_words=800)
        logger.info(f"Text split into {len(chunks)} chunk(s).")
        summaries = []
        for idx, c in enumerate(chunks):
            logger.info(f"Summarizing chunk {idx+1}/{len(chunks)} (words={len(c.split())})")
            chunk_summary = _summarize_chunk(c)
            if chunk_summary:
                summaries.append(chunk_summary)

        final_summary = " ".join(summaries).strip()
        if not final_summary:
            logger.warning("Summary is empty after summarizing all chunks")
            return {"success": False, "error": "Summary is empty."}

        return {"success": True, "summary_text": final_summary}

    except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
        logger.exception("Runtime error during summarization")
        return {"success": False, "error": f"Runtime error during summarization: {str(e)}"}

    except Exception as e:
        logger.exception("Unexpected error during summarization")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
