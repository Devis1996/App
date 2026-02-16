# Tennis Match Insight App (MVP testabile subito)

Hai chiesto: **"come posso testarla?"**

Per evitare blocchi di installazione, questo repo include un **parser MVP in puro Python** (senza dipendenze runtime esterne), così puoi provarlo immediatamente.

## Cosa c'è nel progetto
- `tennis_parser.py`: estrae punteggio, vincitore, avversario, eventi chiave e insight.
- `demo.py`: esempio rapido di esecuzione.
- `tests/test_parse_report.py`: test automatici.

## 1) Test veloce manuale
Esegui:

```bash
python3 demo.py
```

Output atteso (JSON):
- `winner`: `user|opponent|unknown`
- `score.sets`: lista set validi trovati (es. `6-4`, `3-6`, `7-6(7-5)`)
- `opponent`: nome estratto + possibile match con avversario noto
- `extraction_confidence`: confidenza estrazione
- `insights`: spunti pratici di miglioramento

## 2) Test con tuo testo personalizzato
Puoi testare al volo così:

```bash
python3 - <<'PY'
from tennis_parser import parse_report_json

testo = "Ho perso contro Luca Bianchi 4-6 6-7(3-7), troppi doppi falli e poca seconda."
print(parse_report_json(testo))
PY
```

## 3) Test automatici
Esegui:

```bash
pytest -q
```

I test verificano:
- caso completo con punteggio + avversario + insight
- caso ambiguo senza punteggio chiaro

---

## Come interpretare i risultati
- **Confidenza alta**: testo preciso con set chiari e avversario esplicito.
- **Confidenza media/bassa**: pochi dettagli o punteggio ambiguo.
- Se il punteggio non è deducibile, il sistema restituisce `winner: "unknown"`.

---

## Prossimo step (se vuoi la versione “app vera”)
Posso nel prossimo commit trasformarla in app completa con:
1. Backend API (FastAPI)
2. Login JWT
3. Input vocale (Speech-to-Text)
4. Database PostgreSQL
5. Frontend web/mobile minimale
