"""
benchmark_llms.py

Measures generation performance of Qwen3-4B vs Phi-3-Mini using the SourceWell
project's own modules. This script does not reimplement anything: patient data,
calculators, RAG retrieval, prompt templates, citation verification, and model
wrappers are all imported from the project.

What this script contributes:
  - Load one of the four predefined patient scenarios
  - Run the project's calculator pipeline on it
  - Call each engine's generate_explanation() through the real code path
  - Time each call, count output tokens, track peak VRAM
  - Average across N runs and save results to JSON

Run from the sourcewell-project root, with the same environment used by the app:
    python benchmark_llms.py                          # scenario 1, both models, 3 runs
    python benchmark_llms.py --scenario high_risk_middle_aged_male
    python benchmark_llms.py --models qwen
    python benchmark_llms.py --runs 5
    python benchmark_llms.py --explanation-type diabetes
"""

import argparse
import gc
import json
import time
from pathlib import Path

import torch

# --- Project imports -------------------------------------------------------
from data_models.patient_data import PatientData, get_test_scenarios
from calculators.runner import MultiCalculatorRunner
from llm.qwen3_engine import Qwen3Engine
from llm.phi3_engine import Phi3MiniEngine


# ---------------------------------------------------------------------------
# VRAM helpers
# ---------------------------------------------------------------------------

def cuda_available() -> bool:
    return torch.cuda.is_available()


def reset_vram_peak() -> None:
    if cuda_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()


def peak_vram_gb() -> float:
    if not cuda_available():
        return 0.0
    torch.cuda.synchronize()
    return torch.cuda.max_memory_allocated() / 1e9


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


# ---------------------------------------------------------------------------
# Per-model benchmark
# ---------------------------------------------------------------------------

def benchmark_engine(
    engine,
    engine_label: str,
    patient_data: dict,
    risk_results: dict,
    explanation_type: str,
    runs: int,
    output_dir: Path,
    out_file_stem: str,
) -> dict:
    """
    Run the engine's real generate_explanation() `runs` times, measure timing,
    output tokens (via the underlying wrapper's tokenizer), and peak VRAM per run.
    A warmup call is performed first and not counted.
    """
    print(f"\n{'=' * 70}")
    print(f"Benchmarking {engine_label}")
    print(f"{'=' * 70}")

    # Initialise the engine (loads the model)
    reset_vram_peak()
    ok = engine.initialize()
    if not ok:
        raise RuntimeError(f"{engine_label}: engine.initialize() returned False")
    vram_after_load_gb = peak_vram_gb()
    print(f"VRAM after load: {vram_after_load_gb:.3f} GB")

    wrapper = engine.model_wrapper
    tokenizer = wrapper.tokenizer

    # Warmup (not measured)
    print("Warmup run (not measured)...")
    _ = engine.generate_explanation(
        patient_data=patient_data,
        risk_results=risk_results,
        explanation_type=explanation_type,
        include_citations=True,
        strict_verification=False,
    )

    per_run = []
    for i in range(1, runs + 1):
        reset_vram_peak()

        t0 = time.perf_counter()
        result = engine.generate_explanation(
            patient_data=patient_data,
            risk_results=risk_results,
            explanation_type=explanation_type,
            include_citations=True,
            strict_verification=False,
        )
        if cuda_available():
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - t0

        if not result.get("success"):
            raise RuntimeError(
                f"{engine_label} run {i} failed: {result.get('error', 'unknown')}"
            )

        explanation = result.get("explanation", "")
        # Tokenise the final returned explanation with the same model's tokenizer
        output_tokens = len(
            tokenizer(explanation, add_special_tokens=False)["input_ids"]
        )
        tps = safe_div(output_tokens, elapsed)
        seconds_per_output_token = safe_div(elapsed, output_tokens)
        peak_gb = peak_vram_gb()

        print(
            f"Run {i}: {elapsed:.2f}s | {output_tokens} tokens | "
            f"{tps:.1f} tok/s | {seconds_per_output_token:.4f} s/token | "
            f"peak VRAM {peak_gb:.3f} GB"
        )

        # Save generated text for coherence inspection
        (output_dir / f"{out_file_stem}_run{i}.txt").write_text(
            explanation, encoding="utf-8"
        )

        per_run.append({
            "run": i,
            "generation_time_s": round(elapsed, 4),
            "output_tokens": output_tokens,
            "tokens_per_second": round(tps, 3),
            "seconds_per_output_token": round(seconds_per_output_token, 6),
            "peak_vram_gb": round(peak_gb, 4),
            "output_char_len": len(explanation),
            "verification_score": result.get("verification_score"),
            "flagged_sentences": len(result.get("flagged_sentences") or []),
            "sources_used": result.get("context_sources") or len(result.get("citations") or []),
        })

    n = len(per_run)
    avg = {
        "generation_time_s": round(sum(r["generation_time_s"] for r in per_run) / n, 4),
        "output_tokens": round(sum(r["output_tokens"] for r in per_run) / n, 2),
        "tokens_per_second": round(sum(r["tokens_per_second"] for r in per_run) / n, 3),
        "seconds_per_output_token": round(sum(r["seconds_per_output_token"] for r in per_run) / n, 6),
        "peak_vram_gb": round(max(r["peak_vram_gb"] for r in per_run), 4),
    }
    print(
        f"AVG: {avg['generation_time_s']:.2f}s | {avg['output_tokens']} tokens | "
        f"{avg['tokens_per_second']:.1f} tok/s | {avg['seconds_per_output_token']:.4f} s/token | "
        f"max-peak VRAM {avg['peak_vram_gb']:.3f} GB"
    )

    info = wrapper.get_model_info() if hasattr(wrapper, "get_model_info") else {}

    return {
        "engine_label": engine_label,
        "model_id": info.get("model_id"),
        "device": info.get("device"),
        "quantization": info.get("quantization_type"),
        "vram_after_load_gb": round(vram_after_load_gb, 4),
        "runs": per_run,
        "average": avg,
    }


def unload_engine(engine) -> None:
    """Release the engine's wrapper and clear CUDA state."""
    try:
        if getattr(engine, "model_wrapper", None) is not None:
            engine.model_wrapper.unload_model()
    except Exception:
        pass
    del engine
    gc.collect()
    if cuda_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    scenarios = get_test_scenarios()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario", type=str, default="high_risk_middle_aged_male",
        choices=list(scenarios.keys()),
        help="Which predefined patient scenario to benchmark on.",
    )
    parser.add_argument(
        "--explanation-type", type=str, default="general",
        choices=["diabetes", "cardiovascular", "colorectal", "general"],
        help="Which condition-specific prompt template to use.",
    )
    parser.add_argument(
        "--runs", type=int, default=3,
        help="Timed runs per model, excluding warmup. Default: 3.",
    )
    parser.add_argument(
        "--models", type=str, default="qwen,phi3",
        help="Comma-separated model keys to benchmark: qwen, phi3.",
    )
    parser.add_argument(
        "--out", type=str, default="benchmark_results.json",
        help="Output JSON path. Default: benchmark_results.json.",
    )
    args = parser.parse_args()

    scenario_dict = scenarios[args.scenario]
    model_keys = [m.strip() for m in args.models.split(",") if m.strip()]

    output_dir = Path("benchmark_outputs")
    output_dir.mkdir(exist_ok=True)

    print(f"Scenario:         {args.scenario}")
    print(f"Explanation type: {args.explanation_type}")
    print(f"Runs per model:   {args.runs}")
    print(f"Models:           {', '.join(model_keys)}")
    print(f"CUDA available:   {cuda_available()}")
    if cuda_available():
        print(f"GPU:              {torch.cuda.get_device_name(0)}")

    # Build the PatientData object using the project's own class
    patient = PatientData.from_dict(scenario_dict)
    errors = patient.validate()
    if errors:
        raise SystemExit(f"PatientData validation errors: {errors}")

    # Run the project's real risk calculator pipeline
    print("\nRunning MultiCalculatorRunner.run_all_assessments...")
    runner = MultiCalculatorRunner()
    assessment = runner.run_all_assessments(patient)
    if not assessment.get("success"):
        raise SystemExit(f"Calculator run failed: {assessment.get('errors')}")

    # These are what the engines expect
    patient_data_dict = patient.to_calculator_dict()
    risk_results_dict = assessment.get("results", {})
    print(f"Risk results produced for: {list(risk_results_dict.keys())}")

    results = {
        "scenario": args.scenario,
        "explanation_type": args.explanation_type,
        "runs_per_model": args.runs,
        "cuda_available": cuda_available(),
        "gpu_name": torch.cuda.get_device_name(0) if cuda_available() else None,
        "patient_summary": patient.summary(),
        "risk_calculators_run": list(risk_results_dict.keys()),
        "models": {},
    }

    # Benchmark models one at a time so VRAM is fully released between them
    for key in model_keys:
        if key == "qwen":
            engine = Qwen3Engine()
            label = "Qwen3-4B"
        elif key == "phi3":
            engine = Phi3MiniEngine()
            label = "Phi-3-Mini-4k-Instruct"
        else:
            raise ValueError(f"Unknown model key: {key}")

        try:
            results["models"][key] = benchmark_engine(
                engine=engine,
                engine_label=label,
                patient_data=patient_data_dict,
                risk_results=risk_results_dict,
                explanation_type=args.explanation_type,
                runs=args.runs,
                output_dir=output_dir,
                out_file_stem=key,
            )
        finally:
            unload_engine(engine)

    if "qwen" in results["models"] and "phi3" in results["models"]:
        qwen_avg = results["models"]["qwen"]["average"]
        phi3_avg = results["models"]["phi3"]["average"]
        results["comparison"] = {
            "raw_generation_time_ratio_qwen_over_phi3": round(
                safe_div(qwen_avg["generation_time_s"], phi3_avg["generation_time_s"]), 4
            ),
            "normalized_seconds_per_output_token_ratio_qwen_over_phi3": round(
                safe_div(qwen_avg["seconds_per_output_token"], phi3_avg["seconds_per_output_token"]), 4
            ),
            "throughput_tokens_per_second_ratio_qwen_over_phi3": round(
                safe_div(qwen_avg["tokens_per_second"], phi3_avg["tokens_per_second"]), 4
            ),
        }
        print("\nCross-model ratios:")
        print(
            "  Raw avg generation-time ratio (Qwen / Phi-3): "
            f"{results['comparison']['raw_generation_time_ratio_qwen_over_phi3']:.4f}"
        )
        print(
            "  Normalized seconds-per-token ratio (Qwen / Phi-3): "
            f"{results['comparison']['normalized_seconds_per_output_token_ratio_qwen_over_phi3']:.4f}"
        )
        print(
            "  Throughput ratio tok/s (Qwen / Phi-3): "
            f"{results['comparison']['throughput_tokens_per_second_ratio_qwen_over_phi3']:.4f}"
        )

    out_path = Path(args.out)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved results to {out_path.resolve()}")
    print(f"Saved generated text to {output_dir.resolve()}/")


if __name__ == "__main__":
    main()
