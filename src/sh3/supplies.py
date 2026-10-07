"""Deterministic filler-only ammo/healing weighting; no location changes."""
from collections import Counter
from .data import AMMO_WEAPON_PAIRS, ITEM_CLASSIFICATION
AMMO = frozenset(ammo for _, ammo in AMMO_WEAPON_PAIRS) | {'Stun Gun Battery'}
HEALING = frozenset(('Health Drink', 'First-Aid Kit', 'Ampoule'))

def balance_supplies(pool, ammo_weight=100, healing_weight=100):
    if not 25 <= ammo_weight <= 200 or not 25 <= healing_weight <= 200:
        raise ValueError('Supply weights must be between 25 and 200')
    counts = Counter(n for n in pool if n in AMMO | HEALING and ITEM_CLASSIFICATION[n] == 'filler')
    before = dict(sorted(counts.items()))
    # Exact default/equal-weight preservation, including RNG and item order.
    if ammo_weight == healing_weight or not counts:
        return list(pool), dict(before=before, after=before, policy='unchanged')
    names = sorted(counts)
    # Keep at least one of each existing supply type, without introducing
    # an ammo type that was absent from the original pool.
    total = sum(counts.values()); spare = total-len(names)
    weights = {n: counts[n]*(ammo_weight if n in AMMO else healing_weight) for n in names}
    denom = sum(weights.values())
    target = {n: 1 + spare*weights[n]//denom for n in names}
    order = sorted(names,key=lambda n: (-(spare*weights[n]%denom),n))
    for n in order[:total-sum(target.values())]: target[n] += 1
    rewards = iter(n for n in names for _ in range(target[n]))
    result = [next(rewards) if n in counts else n for n in pool]
    return result, dict(before=before, after=target, policy='weighted_filler_minimum_one_per_existing_type')
