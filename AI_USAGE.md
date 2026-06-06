# AI Usage Documentation

## Overview

**InsightSQL** was built with AI-assisted development (Cursor / LLM pair programming) for a hackathon submission. This document records what AI contributed, prompts used, and corrections made.

## What AI helped with

| Component | AI contribution |
|-----------|-----------------|
| Architecture | 7-step agent loop, folder structure, separation of concerns |
| `agents/` | Schema reader, SQL generator, validator, insight generator, LLM client |
| `ui/` | Hackathon-grade CSS, components, loading states |
| `utils/history.py` | Query log + CSV export |
| Sample data | Tamil names, Tamil Nadu locations, Rs pricing |
| Tests | 20+ pytest cases for security and analytics |
| Docs | README, AI_USAGE.md |

## Prompts used

### SQL generation (`prompts/sql_prompt.txt`)

- Schema-grounded SQLite analyst for Indian company data
- Rs amounts, Tamil employee names, Tamil Nadu cities
- SELECT-only, JOIN guidance, monthly `strftime` patterns

### Insight generation (`prompts/insight_prompt.txt`)

- JSON output: insight + chart metadata
- No invented numbers

### Development prompts (Cursor)

- *"Build NL-to-SQL agent with 7-step pipeline for hackathon"*
- *"Add query history, CSV download, loading animations"*
- *"Use Tamil names and Rs instead of dollar"*
- *"Make submission-ready with tests and professional README"*

## AI mistakes and corrections

| Issue | Mistake | Fix |
|-------|---------|-----|
| SQL in markdown fences | Model wrapped SQL in code blocks | `_extract_sql()` + validator strips fences |
| Wrong schema | Old e-commerce tables referenced | Rebuilt `company.db` with departments/employees/products/sales |
| Ollama timeout | Local Llama3 too slow on Windows | Added OpenRouter as default backend |
| OpenRouter 404 | Deprecated `gemini-2.0-flash-001` | Updated to `gemini-2.5-flash` |
| Windows encoding | Emoji caused ascii errors | UTF-8 mode + ASCII-safe HTTP headers |
| Currency | USD `$` in UI | `format_inr()` → **Rs** everywhere |
| Names | Western demo names | CSV updated: Dhana, Priya, Rithan, Yoga, Gopi, Jaya, Dharshana, Gayu, Loki, Koushi, Dharshini |

## Human review checklist

- [x] SQL validator blocks destructive statements (incl. TRUNCATE)
- [x] Read-only SQLite execution
- [x] Query history + CSV export
- [x] Tamil names in seed data
- [x] Rs formatting in KPIs
- [x] pytest suite passes
- [x] README with architecture diagram

## Ethical use

- Generated SQL is always shown to the user
- Query history is session-local (not sent externally except to chosen LLM provider)
- OpenRouter: data sent to cloud API — disclosed in README
- Ollama: fully local option available
