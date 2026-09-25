def _text(value, fallback=""):
    if value is None:
        return fallback

    return str(value).strip()


def _valid_score(value):
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    return 0 <= value <= 5


def _clean_strengths(full_report):
    strengths = (
        full_report.get("strengths")
        or []
    )

    if not isinstance(strengths, list):
        return []

    cleaned = []

    for value in strengths:
        if not isinstance(value, str):
            continue

        value = value.strip()

        if value:
            cleaned.append(value)

    return cleaned


def _clean_criteria(full_report):
    raw_criteria = (
        full_report.get("criteria")
        or {}
    )

    if not isinstance(raw_criteria, dict):
        return []

    criteria = []

    for name, item in raw_criteria.items():
        if not isinstance(item, dict):
            continue

        score = item.get("score")

        if not _valid_score(score):
            continue

        title = str(name).replace(
            "_",
            " ",
        ).strip()

        if not title:
            continue

        criteria.append(
            {
                "title": title,
                "score": score,
            }
        )

    return criteria


def build_short_report(full_report):
    if not isinstance(full_report, dict):
        full_report = {}

    strengths = _clean_strengths(
        full_report
    )

    criteria = _clean_criteria(
        full_report
    )

    edge_strength = (
        strengths[0]
        if strengths
        else ""
    )

    competition_aligned_strength = _text(
        full_report.get(
            "competition_aligned_strength"
        ),
        "",
    )

    message = _text(
        full_report.get(
            "message"
        ),
        "",
    )

    return {
        "competition": _text(
            full_report.get(
                "competition"
            ),
            "",
        ),
        "stage": _text(
            full_report.get(
                "stage"
            ),
            "",
        ),
        "edge_strength_assessment": edge_strength,
        "competition_aligned_strength": (
            competition_aligned_strength
        ),
        "strength_by_criterion": criteria,
        "decision": full_report.get(
            "decision"
        ),
        "message": message,
    }


def public_evaluation_response(
    evaluation_id,
    short_report,
):
    return {
        "evaluation_id": evaluation_id,
        "short_report": short_report,
        "full_report_available_after_mentor_review": True,
    }





















# def _text(value, fallback=""):
#     if value is None:
#         return fallback

#     return str(value).strip()


# def build_short_report(full_report):
#     criteria = []

#     for name, item in (
#         full_report.get("criteria") or {}
#     ).items():
#         if not isinstance(item, dict):
#             continue

#         criteria.append(
#             {
#                 "title": str(name).replace("_", " "),
#                 "score": item.get("score"),
#             }
#         )

#     strengths = full_report.get("strengths") or []

#     if strengths:
#         edge_strength = _text(
#             strengths[0],
#             "Your work has a promising foundation.",
#         )
#     else:
#         edge_strength = (
#             "Your assessment is complete, but mentor review is required "
#             "before detailed strengths are confirmed."
#         )

#     return {
#         "competition": full_report.get("competition"),
#         "stage": full_report.get("stage"),
#         "edge_strength_assessment": edge_strength,
#         "competition_aligned_strength": (
#             "Your project was assessed against the selected competition "
#             "and stage. The result is advisory and requires mentor review."
#         ),
#         "strength_by_criterion": criteria,
#         "decision": full_report.get("decision"),
#         "message": (
#             "Your short assessment is ready. A UniVisory mentor can provide "
#             "the detailed report and improvement priorities."
#         ),
#     }


# def public_evaluation_response(evaluation_id, short_report):
#     return {
#         "evaluation_id": evaluation_id,
#         "short_report": short_report,
#         "full_report_available_after_mentor_review": True,
#     }