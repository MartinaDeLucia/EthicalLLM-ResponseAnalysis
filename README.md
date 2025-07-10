# EthicalLLM-ResponseAnalysis

Materiali a supporto della tesi triennale sull’interazione tra modelli linguistici e contenuti sensibili: 
**"Un’Analisi Empirica delle Capacità dei Large Language Model nella Gestione di Contenuti Sensibili"**.

Il repository raccoglie i materiali sviluppati per l’esperimento descritto nella tesi, finalizzato ad analizzare la qualità comunicativa e la responsabilità etica con cui tre modelli linguistici open-source — Meta-LLaMA 3 8B Instruct, Qwen2 7B Instruct e DeepSeek 7B Chat — rispondono a prompt sensibili. Include il corpus di domande annotate, le risposte generate da ciascun modello e lo script utilizzato per automatizzare l’interrogazione tramite LM Studio.

---

## 📁 Struttura del repository

- `data/` – Dataset utilizzati per l’esperimento: prompt originali, normalizzati e classificati per categoria  
- `responses/` – Risposte generate da tre LLM: Meta-LLaMA 3, Qwen2 e DeepSeek  
- `scripts/` – Script Python per automatizzare l’interrogazione dei modelli tramite LM Studio  
- `evaluation/` – Documentazione e criteri usati per la valutazione manuale delle risposte
