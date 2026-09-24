def _text(value, fallback=""):
    if value is None:
        return fallback

    return str(value).strip()


def build_short_report(full_report):
    criteria = []

    for name, item in (
        full_report.get("criteria") or {}
    ).items():
        if not isinstance(item, dict):
            continue

        criteria.append(
            {
                "title": str(name).replace("_", " "),
                "score": item.get("score"),
            }
        )

    strengths = full_report.get("strengths") or []

    if strengths:
        edge_strength = _text(
            strengths[0],
            "Your work has a promising foundation.",
        )
    else:
        edge_strength = (
            "Your assessment is complete, but mentor review is required "
            "before detailed strengths are confirmed."
        )

    return {
        "competition": full_report.get("competition"),
        "stage": full_report.get("stage"),
        "edge_strength_assessment": edge_strength,
        "competition_aligned_strength": (
            "Your project was assessed against the selected competition "
            "and stage. The result is advisory and requires mentor review."
        ),
        "strength_by_criterion": criteria,
        "decision": full_report.get("decision"),
        "message": (
            "Your short assessment is ready. A UniVisory mentor can provide "
            "the detailed report and improvement priorities."
        ),
    }


def public_evaluation_response(evaluation_id, short_report):
    return {
        "evaluation_id": evaluation_id,
        "short_report": short_report,
        "full_report_available_after_mentor_review": True,
    }