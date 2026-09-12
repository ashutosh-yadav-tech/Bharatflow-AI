"""
evaluation.py
-------------
Addresses the gap flagged in the design review: a system whose value
proposition is "trustworthy explanation" needs a real accuracy number, not
just plausible-looking demo output. This runs the actual pipeline
(detection -> agent -> diagnosis) against simulated shipments where the
true cause is known but withheld from the agent, in 'eval' mode (simulated
weather, so results are reproducible run to run for a given seed).
"""

from concurrent.futures import ThreadPoolExecutor
from data_generator import generate_batch
from detection import evaluate_shipment
from agent import run_investigation


def _eval_single(ship, report) -> dict:
    diagnosis = run_investigation(ship, report, mode="eval")
    truth = set(ship.ground_truth_causes) if ship.ground_truth_causes else {"unexplained"}
    predicted = diagnosis.get("primary_cause", "unexplained")
    is_correct = predicted in truth
    return {
        "shipment_id": ship.id,
        "ground_truth": sorted(truth),
        "predicted_primary_cause": predicted,
        "correct": is_correct,
        "confidence": diagnosis.get("confidence"),
        "engine": diagnosis.get("engine"),
    }


def run_evaluation(n_shipments: int = 5, seed: int = 7) -> dict:
    shipments = generate_batch(n_shipments, exception_prob=0.6, seed=seed)
    flagged = []
    for ship in shipments:
        report = evaluate_shipment(ship)
        if report["is_flagged"]:
            flagged.append((ship, report))

    # Run evaluations concurrently to ensure snappy response and prevent HTTP timeouts
    max_workers = min(3, max(1, len(flagged))) if flagged else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda pair: _eval_single(pair[0], pair[1]), flagged))

    correct_top1 = sum(1 for r in results if r["correct"])
    accuracy = round(correct_top1 / len(flagged), 3) if flagged else None

    return {
        "n_generated": n_shipments,
        "n_flagged": len(flagged),
        "top1_accuracy": accuracy,
        "details": results,
    }
