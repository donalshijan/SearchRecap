"""
Batch inference processing module for InferenceManager.
Handles processing large datasets in batches using OpenAI's API.
Includes both sequential and concurrent implementations.
"""

import json
import os
from pathlib import Path
import asyncio
import time
import sys
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

from InferenceManager.config import (
    BATCH_SIZE,
    DATA_DESCRIPTION,
    DATA_LABEL,
    MODEL,
    TASK_DESCRIPTION,
    TASK_INSTRUCTIONS,
)
from InferenceManager.utils import (
    generate_dynamic_prompt,
    load_data_items,
    load_prompt,
    save_json_file,
    validate_json_structure,
)


# ======================================================
# ================ Helper / Shared Methods =============
# ======================================================

def print_progress_bar(iteration, total, prefix='', suffix='', batch_time=None, length=40, fill='█', empty='-', decimals=1):
    """
    Simple ASCII progress bar using print statements.
    """
    percent = f"{100 * (iteration / float(total)):.{decimals}f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + empty * (length - filled_length)
    bt = f" | Batch Processing Time: {batch_time:.2f}s" if batch_time is not None else ""
    # clear the line before reprinting
    sys.stdout.write('\r\033[K') 
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}%{bt} {suffix}')
    sys.stdout.flush()
    if iteration >= total:
        print()  # move to next line after completion


def process_batch(client: OpenAI, system_prompt: str, batch: list[dict], batch_id: int) -> list[dict]:
    """
    Send one batch of data items to the LLM and return filtered results.
    Sequential implementation.
    """
    user_prompt: str = "Here is the batch of data items:\n\n" + "\n".join(
        f"- {json.dumps(item, ensure_ascii=False)}" for item in batch
    )

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.output_text
    
    if content is None:
        print(f"[Batch {batch_id}] No content in response")
        return []

    try:
        parsed: list[dict] = json.loads(content)
        if not isinstance(parsed, list) or not all(isinstance(x, dict) for x in parsed):
            raise ValueError("Expected list of dicts output.")
        return parsed
    except Exception as e:
        print(f"[Batch {batch_id}] Parsing error: {e}")
        print("Raw output:", content)
        return []


# ======================================================
# ================ Sequential Version ==================
# ======================================================

def run_batch_inference(input_file: str | Path, output_file: str | Path, prompt_file: str | Path) -> None:
    """
    Run batch inference sequentially on the specified input file.
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    prompt_path = Path(prompt_file)

    if not validate_json_structure(input_path, DATA_LABEL):
        raise ValueError(
            f"Invalid JSON structure in {input_path}. "
            f"Expected a list of items or a dictionary with a list under the '{DATA_LABEL}' key."
        )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OSError("OPENAI_API_KEY not set in environment or .env file")

    client = OpenAI(api_key=api_key)
    data_items: list[dict] = load_data_items(input_path, DATA_LABEL)
    prompt_template: str = load_prompt(prompt_path)
    config = {
        "DATA_LABEL": DATA_LABEL,
        "DATA_DESCRIPTION": DATA_DESCRIPTION,
        "TASK_DESCRIPTION": TASK_DESCRIPTION,
        "TASK_INSTRUCTIONS": TASK_INSTRUCTIONS,
    }
    system_prompt: str = generate_dynamic_prompt(prompt_template, config)

    print(f"Loaded {len(data_items)} {DATA_LABEL}.")
    print(f"Processing with task: {TASK_DESCRIPTION}")
    results: list[dict] = []
    total_items = len(data_items[:100])
    total_batches = (total_items + BATCH_SIZE - 1) // BATCH_SIZE
    start_time = time.time()
    print(f"\n🔹 Processing {total_batches} batches...\n")
    print_progress_bar(
                iteration=0,
                total=total_batches,
                prefix=f"Batch {0}/{total_batches}",
                suffix=f"Elapsed: {0:.1f}s  Items_Processed: {0}",
                batch_time=0,
                length=40
            )
    for i in range(0, len(data_items[:100]), BATCH_SIZE):
        batch: list[dict] = data_items[i : i + BATCH_SIZE]
        batch_id: int = i // BATCH_SIZE + 1
        batch_start = time.time()
        filtered: list[dict] = process_batch(client, system_prompt, batch, batch_id)
        results.extend(filtered)
        elapsed = time.time() - start_time
        batch_time = time.time() - batch_start

        print_progress_bar(
            iteration=(i + len(batch)),
            total=total_items,
            prefix=f"Batch {batch_id}/{total_batches}",
            suffix=f"Elapsed: {elapsed:.1f}s",
            batch_time=batch_time,
            length=40
        )

    save_json_file({f"Filtered_{DATA_LABEL}": results}, output_path)
    print(f"✅ Done. Extracted and processed {len(results)} matching {DATA_LABEL} → {output_file}")


# ======================================================
# ================ Concurrent Version ==================
# ======================================================

async def process_batch_async(client: AsyncOpenAI, system_prompt: str, batch: list[dict], batch_id: int) -> list[dict]:
    """
    Async version of process_batch using AsyncOpenAI.
    """
    user_prompt: str = "Here is the batch of data items:\n\n" + "\n".join(
        f"- {json.dumps(item, ensure_ascii=False)}" for item in batch
    )

    try:
        resp = await client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = resp.output_text
        if not content:
            print(f"[Batch {batch_id}] Empty content")
            return []
        parsed = json.loads(content)
        if not isinstance(parsed, list):
            raise ValueError("Expected list of dicts output.")
        return parsed
    except Exception as e:
        print(f"[Batch {batch_id}] Error: {e}")
        return []


async def run_batch_inference_concurrently(
    input_file: str | Path,
    output_file: str | Path,
    prompt_file: str | Path,
    concurrency: int = 10
) -> None:
    """
    Run batch inference concurrently using asyncio for higher throughput.
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    prompt_path = Path(prompt_file)

    if not validate_json_structure(input_path, DATA_LABEL):
        raise ValueError(
            f"Invalid JSON structure in {input_path}. "
            f"Expected a list of items or a dictionary with a list under the '{DATA_LABEL}' key."
        )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OSError("OPENAI_API_KEY not set in environment or .env file")

    client = AsyncOpenAI(api_key=api_key)
    data_items: list[dict] = load_data_items(input_path, DATA_LABEL)
    prompt_template: str = load_prompt(prompt_path)
    config = {
        "DATA_LABEL": DATA_LABEL,
        "DATA_DESCRIPTION": DATA_DESCRIPTION,
        "TASK_DESCRIPTION": TASK_DESCRIPTION,
        "TASK_INSTRUCTIONS": TASK_INSTRUCTIONS,
    }
    system_prompt: str = generate_dynamic_prompt(prompt_template, config)

    print(f"Loaded {len(data_items)} {DATA_LABEL}.")
    print(f"Processing with task: {TASK_DESCRIPTION}")
    
    results: list[dict] = []
    total_items = len(data_items[:100])
    total_batches = (total_items + BATCH_SIZE - 1) // BATCH_SIZE
    semaphore = asyncio.Semaphore(concurrency)
    progress_lock = asyncio.Lock()        # prevent overlapping prints
    completed_batches = 0                 # shared atomic progress counter
    start_time = time.time()
    print(f"\n🔹 Processing {total_batches} batches...\n")
    print_progress_bar(
                    iteration=completed_batches,
                    total=total_batches,
                    prefix=f"Batch {0}/{total_batches}",
                    suffix=f"Elapsed: {0:.1f}s  Items_Processed: {0}",
                    batch_time=0,
                    length=40
                )
    async def sem_task(batch, batch_id):
        nonlocal completed_batches
        async with semaphore:
            batch_start = time.time()
            filtered = await process_batch_async(client, system_prompt, batch, batch_id)
            results.extend(filtered)
            
             # Atomic progress update
            async with progress_lock:
                completed_batches += 1
                batch_time = time.time() - batch_start
                elapsed = time.time() - start_time
                items_processed = min(completed_batches * BATCH_SIZE, total_items)
                print_progress_bar(
                    iteration=completed_batches,
                    total=total_batches,
                    prefix=f"Batch {batch_id}/{total_batches}",
                    suffix=f"Elapsed: {elapsed:.1f}s  Items_Processed: {items_processed}",
                    batch_time=batch_time,
                    length=40
                )

    tasks = []
    for i in range(0, len(data_items[:100]), BATCH_SIZE):
        batch = data_items[i : i + BATCH_SIZE]
        batch_id = i // BATCH_SIZE + 1
        tasks.append(asyncio.create_task(sem_task(batch, batch_id)))

    await asyncio.gather(*tasks)
    save_json_file({f"Filtered_{DATA_LABEL}": results}, output_path)
    print(f"✅ Done. Extracted and processed {len(results)} matching {DATA_LABEL} → {output_file}")


# ======================================================
# ================ Entry Point =========================
# ======================================================

if __name__ == "__main__":
    from config import INPUT_FILE, OUTPUT_FILE, PROMPT_FILE
    mode = sys.argv[1] if len(sys.argv) > 1 else "sequential"

    if mode == "concurrent":
        asyncio.run(run_batch_inference_concurrently(INPUT_FILE, OUTPUT_FILE, PROMPT_FILE, concurrency=10))
    else:
        run_batch_inference(INPUT_FILE, OUTPUT_FILE, PROMPT_FILE)
