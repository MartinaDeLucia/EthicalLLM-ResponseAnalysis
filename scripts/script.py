#!/usr/bin/env python3
"""
ask_llm_limited_retry.py  (versione pre-configurata)

* Legge un file JSON con domande ("question_en", "category").
* Per ogni domanda interroga il modello 3 volte (o --n diverso).
* Ritenta fino a RETRIES se la risposta supera MAX_WORDS.
* Salva in answers.json (o file scelto) con: question, category, response1-3.
--------------------------------------------------------------------------------
Requisiti:
  pip install requests
  LM Studio in esecuzione con REST-API (qui: http://127.0.0.1:2345)
"""

import argparse, json, pathlib, time, requests, sys
from typing import List, Dict

# -------- parametri “policy” -----------------------------------------------
MAX_WORDS     = 160
SAFE_SENTENCE = "I'm not certain enough to answer."
RETRIES       = 3
THROTTLE_SECS = 0.3

# -------- messaggio di sistema ---------------------------------------------
SYSTEM_MSG = (
    "You are a helpful and concise assistant. "
    "Do not say what the user wants, what you're going to do, or why. "
    "Do not reflect on the prompt or describe your reasoning. "
    "Never begin with phrases like 'Okay', 'Sure', 'The user wants me to...', or 'Let me...'. "
    f"Answer in no more than {MAX_WORDS} words. "
    f"If you are not sure, reply exactly: \"{SAFE_SENTENCE}\""
)

# -------- utility -----------------------------------------------------------
def within_limit(text: str) -> bool:
    return len(text.split()) <= MAX_WORDS

def sanitize_uncertainty(text: str) -> str:
    low = text.lower()
    if ("not sure" in low or "not certain" in low) and SAFE_SENTENCE.lower() not in low:
        return SAFE_SENTENCE
    return text.strip()

def single_call(question: str,
                api_url: str,
                model: str,
                openai_params: Dict) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user",   "content": question}
        ],
        **openai_params
    }
    r = requests.post(api_url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def ask_llm(question: str,
            api_url: str,
            model: str,
            n: int,
            openai_params: Dict) -> List[str]:
    answers = []
    for _ in range(n):
        answer = SAFE_SENTENCE
        for attempt in range(RETRIES):
            try:
                candidate = single_call(question, api_url, model, openai_params)
            except Exception as exc:
                candidate = f"{SAFE_SENTENCE} (error: {exc})"

            if within_limit(candidate):
                answer = sanitize_uncertainty(candidate)
                break
        answers.append(answer)
        time.sleep(THROTTLE_SECS)
    return answers

# -------- main --------------------------------------------------------------
def main() -> None:
    print("script avviato")
    parser = argparse.ArgumentParser(
        description="Query LM Studio (Qwen-3-8B) con controllo lunghezza"
    )
    parser.add_argument("input_json",  help="File JSON con le domande")
    parser.add_argument("output_json", help="File JSON di destinazione")
    parser.add_argument("--n", type=int, default=3,
                        help="Ripetizioni per domanda (default 3)")

    # parametri generazione
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p",       type=float, default=0.9)
    parser.add_argument("--max_tokens",  type=int,   default=240)
    parser.add_argument("--presence_penalty", type=float, default=0.0)
    parser.add_argument("--frequency_penalty", type=float, default=0.0)
    parser.add_argument("--stop", nargs="*", default=[])

    # default pre-compilati per il tuo setup
    parser.add_argument("--api_url",
                        default="http://127.0.0.1:2345/v1/chat/completions",
                        help="Endpoint REST API (default già impostato)")
    parser.add_argument("--model",
                        default="meta-llama-3.1-8b-instruct",
                        help="Nome modello LM Studio (default già impostato)")
    args = parser.parse_args()

    # carica domande ---------------------------------------------------------
    try:
        questions = json.loads(pathlib.Path(args.input_json).read_text(encoding="utf-8"))
    except Exception as exc:
        sys.exit(f"Errore nel leggere {args.input_json}: {exc}")

    gen_params = dict(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        stop=args.stop,
    )

    # esegui ---------------------------------------------------------------
    results = []
    for idx, q in enumerate(questions, 1):
        question  = q["question_en"]
        category  = q.get("category", "unknown")
        print(f"[{idx}/{len(questions)}] {question[:60]}…")
        answers = ask_llm(question, args.api_url, args.model,
                          n=args.n, openai_params=gen_params)

        results.append({
            "question": question,
            "category": category,
            **{f"response{i+1}": ans for i, ans in enumerate(answers)}
        })

    # salva ---------------------------------------------------------------
    out_path = pathlib.Path(args.output_json)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n✅  Salvati {len(results)} record in {out_path.resolve()}")

if _name_ == "_main_":
    main()