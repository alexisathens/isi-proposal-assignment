#!/usr/bin/env python3
"""
ips_embed_proposals.py

Purpose:
  Create master JSON with IPS proposals enriched with text embeddings.
  Modified to work with Ollama instead of OpenAI.

Example:
  python ips_embed_proposals.py \
    --proposals proposals.csv \
    --members proposal_members.csv \
    --descriptions proposal_descriptions.csv \
    --out proposals_with_embeddings.json
"""


from __future__ import annotations

import os
import csv
import json
import time
import argparse
from typing import List, Dict, Any

import backoff  # type: ignore
import requests

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://10.0.9.83:11434")
EMBED_MODEL = os.getenv("IPS_EMBED_MODEL", "nomic-embed-text")  # or "mxbai-embed-large"
SLEEP_BETWEEN = float(os.getenv("IPS_EMBED_SLEEP_SEC", "0.5"))


def read_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="latin-1", newline="") as f:
        return list(csv.DictReader(f, delimiter=';'))


def load_json(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: List[Dict[str, Any]]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def combine_text(proposal: Dict[str, Any], participants: List[Dict[str, Any]], description: Dict[str, Any] | None) -> str:
    parts: List[str] = []
    parts.append("\n".join(f"{k}: {v}" for k, v in proposal.items() if v))
    if participants:
        parts.append("Participants:\n" + "\n".join(f"{p.get('Name','')} ({p.get('Role','')})" for p in participants))
    if description:
        brief = description.get("Brief Description", "")
        long = description.get("WSC Proposal Description", "")
        parts.append(f"Brief Description: {brief}\nDetailed Description: {long}")
    return "\n".join(parts)


def build_lookup(rows: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        k = str(r.get(key, ""))
        out.setdefault(k, []).append(r)
    return out


def single_lookup(rows: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        k = str(r.get(key, ""))
        out[k] = r
    return out


@backoff.on_exception(backoff.expo, Exception, max_time=120)
def embed_text(text: str) -> List[float]:
    """
    Generate embeddings using Ollama's API.
    
    Args:
        text: Text to embed
    
    Returns:
        List of floats representing the embedding vector
    """
    url = f"{OLLAMA_HOST}/api/embeddings"
    payload = {
        "model": EMBED_MODEL,
        "prompt": text
    }
    
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    
    data = response.json()
    return data["embedding"]


def check_ollama_connection() -> None:
    """Verify that Ollama is running and the model is available."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        if not any(EMBED_MODEL in name for name in model_names):
            print(f"Warning: Model '{EMBED_MODEL}' not found in Ollama.")
            print(f"Available models: {', '.join(model_names)}")
            print(f"\nTo pull the model, run: ollama pull {EMBED_MODEL}")
            raise RuntimeError(f"Model {EMBED_MODEL} not available")
        
        print(f"✓ Connected to Ollama at {OLLAMA_HOST}")
        print(f"✓ Using model: {EMBED_MODEL}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_HOST}. "
            "Make sure Ollama is running with: ollama serve"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Embed IPS proposals into a master JSON file (Ollama version)")
    ap.add_argument("--proposals", default="proposals.csv", help="proposals.csv")
    ap.add_argument("--members", default="proposal_members.csv", help="proposal_members.csv")
    ap.add_argument("--descriptions", default="descriptions.csv", help="descriptions.csv")
    ap.add_argument("--out", default="proposals_with_embeddings.json", help="output JSON path")
    args = ap.parse_args()

    # Check Ollama connection and model availability
    check_ollama_connection()

    proposals = read_csv(args.proposals)
    participants = read_csv(args.members)
    descriptions = read_csv(args.descriptions)

    if proposals:
        print("Columnas encontradas en proposals.csv:")
        print(list(proposals[0].keys()))
        print("\nPrimera fila de ejemplo:")
        print(proposals[0])

    by_id_existing = {str(x.get("Proposal ID")): x for x in load_json(args.out)}
    have_ids = set(by_id_existing.keys())

    parts_by_pid = build_lookup(participants, "Proposal ID")
    desc_by_pid = single_lookup(descriptions, "Proposal ID")

    out: List[Dict[str, Any]] = list(by_id_existing.values())

    total = len([p for p in proposals if str(p.get("Proposal ID"))])
    processed = 0

    for row in proposals:
        pid = str(row.get("Proposal ID"))
        if not pid:
            continue
        if pid in have_ids and by_id_existing[pid].get("embedding"):
            processed += 1
            print(f"[{processed}/{total}] Skipping {pid} (already embedded)")
            continue
        
        text = combine_text(row, parts_by_pid.get(pid, []), desc_by_pid.get(pid))
        print(f"[{processed + 1}/{total}] Embedding proposal {pid}...")
        emb = embed_text(text)
        
        payload = {
            **row,
            "Participants": parts_by_pid.get(pid, []),
            "Description": desc_by_pid.get(pid, {}),
            "embedding": emb,
        }
        # replace or append
        if pid in have_ids:
            # update existing
            idx = next(i for i, v in enumerate(out) if str(v.get("Proposal ID")) == pid)
            out[idx] = payload
        else:
            out.append(payload)
            have_ids.add(pid)
        
        save_json(args.out, out)
        processed += 1
        time.sleep(SLEEP_BETWEEN)

    print(f"\n✓ Wrote {len(out)} records to {args.out}")


if __name__ == "__main__":
    main()