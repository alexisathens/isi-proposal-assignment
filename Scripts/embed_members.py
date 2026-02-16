#!/usr/bin/env python3
"""
ips_embed_members.py

Purpose:
  Create JSON with members enriched with text embeddings based on their Expertise.

Example:
  python ips_embed_members.py \
    --members members.csv \
    --out members_with_embeddings.json
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
EMBED_MODEL = os.getenv("IPS_EMBED_MODEL", "nomic-embed-text")
SLEEP_BETWEEN = float(os.getenv("IPS_EMBED_SLEEP_SEC", "0.5"))


def read_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="latin-1", newline="") as f:
        # Detectar delimitador automáticamente
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        return list(csv.DictReader(f, delimiter=delimiter))


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


def combine_member_text(member: Dict[str, Any]) -> str:
    """Combine member information into text for embedding."""
    parts: List[str] = []
    
    # Add basic info
    member_id = member.get("ID", "")
    members_list = member.get("Members", "")
    association = member.get("Association", "") or member.get("Association", "")
    expertise = member.get("Expertise", "")
    
    if member_id:
        parts.append(f"ID: {member_id}")
    if members_list:
        parts.append(f"Members: {members_list}")
    if association:
        parts.append(f"Association: {association}")
    if expertise:
        parts.append(f"Expertise: {expertise}")
    
    return "\n".join(parts)


@backoff.on_exception(backoff.expo, Exception, max_time=120)
def embed_text(text: str) -> List[float]:
    """Generate embeddings using Ollama's API."""
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
    ap = argparse.ArgumentParser(description="Embed members into a JSON file with Ollama")
    ap.add_argument("--members", default="members.csv", help="members.csv")
    ap.add_argument("--out", default="members_with_embeddings.json", help="output JSON path")
    args = ap.parse_args()

    # Check Ollama connection
    check_ollama_connection()

    # Load data
    members = read_csv(args.members)
    
    # Debug: show columns
    if members:
        print("\nColumnas encontradas en members.csv:")
        print(list(members[0].keys()))
    
    # Load existing embeddings if any
    by_id_existing = {str(x.get("ID")): x for x in load_json(args.out)}
    have_ids = set(by_id_existing.keys())

    out: List[Dict[str, Any]] = list(by_id_existing.values())

    total = len([m for m in members if str(m.get("ID", "")).strip()])
    processed = 0

    for row in members:
        member_id = str(row.get("ID", "")).strip()
        
        # Skip if no ID
        if not member_id or member_id == "None":
            continue
        
        # Skip if already embedded
        if member_id in have_ids and by_id_existing.get(member_id, {}).get("embedding"):
            processed += 1
            print(f"[{processed}/{total}] Skipping member {member_id} (already embedded)")
            continue
        
        # Check if member has expertise to embed
        expertise = str(row.get("Expertise", "")).strip()
        if not expertise:
            print(f"[{processed + 1}/{total}] Skipping member {member_id} (no expertise)")
            processed += 1
            continue
        
        # Combine text and generate embedding
        text = combine_member_text(row)
        print(f"[{processed + 1}/{total}] Embedding member {member_id}...")
        emb = embed_text(text)
        
        # Create payload with all original data plus embedding
        payload = {
            **row,
            "embedding": emb,
        }
        
        # Replace or append
        if member_id in have_ids:
            idx = next(i for i, v in enumerate(out) if str(v.get("ID")) == member_id)
            out[idx] = payload
        else:
            out.append(payload)
            have_ids.add(member_id)
        
        save_json(args.out, out)
        processed += 1
        time.sleep(SLEEP_BETWEEN)

    print(f"\n✓ Wrote {len(out)} records to {args.out}")


if __name__ == "__main__":
    main()