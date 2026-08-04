"""
Business logic for recommending the best shipping box for an order.

Rules (per the build guide):
  1. The product must fit inside the box (each dimension <= box dimension).
  2. The product weight must not exceed the box's max_weight.
  3. Among all boxes that fit, the lowest-cost box wins.
  4. If there is a tie on cost, the box with the smallest unused (wasted)
     volume wins.
  5. If no box fits, return None.
"""
from decimal import Decimal
from typing import Iterable, Optional

from .models import Box, Product


def recommend_box(length: Decimal, width: Decimal, height: Decimal,
                   weight: Decimal, boxes: Iterable[Box]) -> Optional[Box]:
    """Return the cheapest box that fits the given product dimensions and
    weight; ties are broken by the smallest unused (wasted) volume.

    Returns None if no box in `boxes` can accommodate the product.
    """
    product_volume = length * width * height
    candidates = []

    for box in boxes:
        fits_dimensions = (
            length <= box.length and width <= box.width and height <= box.height
        )
        fits_weight = weight <= box.max_weight
        if fits_dimensions and fits_weight:
            wasted_volume = box.volume() - product_volume
            candidates.append((box.cost, wasted_volume, box.pk, box))

    if not candidates:
        return None

    candidates.sort(key=lambda c: (c[0], c[1], c[2]))
    return candidates[0][3]


def combined_requirements(products: Iterable[Product]):
    """Reduce a set of products in one order into a single bounding
    requirement (length, width, height, weight) that a single box must
    satisfy.

    Heuristic: items are assumed to be packed side by side on the same
    footprint (so the box needs the largest length and width of any
    single item) and stacked vertically (so heights and weights sum).
    This keeps the packing model simple and conservative — it will
    never under-estimate what a box needs to hold.
    """
    products = list(products)
    if not products:
        return None

    length = max(p.length for p in products)
    width = max(p.width for p in products)
    height = sum((p.height for p in products), Decimal('0'))
    weight = sum((p.weight for p in products), Decimal('0'))
    return length, width, height, weight


def recommend_box_for_products(products: Iterable[Product], boxes: Iterable[Box]) -> Optional[Box]:
    """Convenience wrapper: combine a set of order products into one
    requirement, then recommend the best-fit box for it."""
    requirements = combined_requirements(products)
    if requirements is None:
        return None
    length, width, height, weight = requirements
    return recommend_box(length, width, height, weight, boxes)
