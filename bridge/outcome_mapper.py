"""Map GPTMEAi results back into SEMASCRIPT outcome packages."""


def map_gptmeai_result_to_semascript_outcome(result):
    """Return a v0.1 placeholder outcome package.

    Real result translation belongs to a future execution-enabled version.
    """
    source_preview_id = ""
    if isinstance(result, dict):
        source_preview_id = result.get("preview_id") or result.get("source_preview_id", "")

    return {
        "version": "0.1",
        "source_preview_id": source_preview_id,
        "status": "placeholder",
        "dry_run": True,
        "result": {
            "message": "GPTMEAi execution result mapping is reserved for a future version.",
            "input_type": type(result).__name__,
        },
        "metadata": {
            "adapter": "GPTMEAi-SEMASCRIPT",
            "v0_1_execution_enabled": False,
        },
    }
