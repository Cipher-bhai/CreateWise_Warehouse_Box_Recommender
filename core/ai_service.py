"""
Free AI integration (Step 8 of the build guide): generate a one-sentence,
human-readable explanation of why a particular box was recommended for a
set of products.

Uses Google Gemini's free tier when GEMINI_API_KEY is configured. If the
key is missing, the package isn't installed, or the API call fails for
any reason (offline, rate-limited, quota exceeded), we fall back to a
deterministic rule-based sentence — the app always works, with or
without network access to an AI provider.
"""
import logging
from decimal import Decimal
from typing import Iterable

from django.conf import settings

from .models import Box, Product

logger = logging.getLogger(__name__)


def _fallback_explanation(box: Box, length: Decimal, width: Decimal,
                           height: Decimal, weight: Decimal) -> str:
    wasted = box.volume() - (length * width * height)
    return (
        f"'{box.name}' was selected because it is the lowest-cost box "
        f"(₹{box.cost}) that fits the {length}×{width}×{height} cm, "
        f"{weight} kg shipment within its {box.max_weight} kg limit, "
        f"leaving about {wasted:.0f} cm³ of unused space."
    )


def explain_recommendation(products: Iterable[Product], box: Box) -> str:
    """Return a one-sentence explanation for why `box` fits `products`.

    Always returns a usable string — never raises — so callers can call
    this unconditionally right after recommend_box() without wrapping
    every call site in its own try/except.
    """
    products = list(products)
    length = max((p.length for p in products), default=Decimal('0'))
    width = max((p.width for p in products), default=Decimal('0'))
    height = sum((p.height for p in products), Decimal('0'))
    weight = sum((p.weight for p in products), Decimal('0'))

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key or box is None:
        if box is None:
            return "No box in the catalog is large enough or light enough to fit this order — add a bigger box or split the shipment."
        return _fallback_explanation(box, length, width, height, weight)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"In one short sentence, explain why box '{box.name}' "
            f"({box.length}x{box.width}x{box.height} cm, {box.max_weight} kg limit, "
            f"cost {box.cost}) is a good fit for a shipment measuring "
            f"{length}x{width}x{height} cm and weighing {weight} kg."
        )
        response = model.generate_content(prompt)
        text = (response.text or '').strip()
        return text or _fallback_explanation(box, length, width, height, weight)
    except Exception:  # noqa: BLE001 — any failure falls back gracefully
        logger.warning('AI explanation generation failed; using rule-based fallback.', exc_info=True)
        return _fallback_explanation(box, length, width, height, weight)
