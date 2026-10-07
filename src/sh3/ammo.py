"""Redistribute only SH3 ammo filler after the seed's progression is final."""
from collections import Counter

from BaseClasses import ItemClassification
from .data import AMMO_WEAPON_PAIRS, AMMO_VANILLA_COUNTS


def allocate(total, ranked_weapons):
    """Assign the vanilla count shares to guns in acquisition order."""
    weights = sorted(AMMO_VANILLA_COUNTS.values(), reverse=True)[:len(ranked_weapons)]
    if not weights:
        return {}
    denominator = sum(weights)
    counts = [total * weight // denominator for weight in weights]
    order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
    for i in order[:total - sum(counts)]:
        counts[i] += 1
    ammo_for = dict(AMMO_WEAPON_PAIRS)
    return {ammo_for[gun]: count for gun, count in zip(ranked_weapons, counts)}


def match_rewards(world, locations, counts):
    """Find a complete permitted assignment, or leave the original pool intact.

    Matching rather than a greedy fill preserves item-name/locality restrictions
    even when only some ammo types are legal in a particular location.
    """
    templates = {name: world.create_item(name) for name in counts}
    allowed = {name: [i for i, loc in enumerate(locations) if loc.item_rule(item)]
               for name, item in templates.items()}
    tokens = [name for name in sorted(counts, key=lambda name: (len(allowed[name]), name))
              for _ in range(counts[name])]
    assigned = {}

    def place(name, seen):
        for i in allowed[name]:
            if i in seen:
                continue
            seen.add(i)
            if i not in assigned or place(assigned[i], seen):
                assigned[i] = name
                return True
        return False

    if not all(place(name, set()) for name in tokens):
        return None
    return [assigned[i] for i in range(len(locations))]


def rebalance_ammo(multiworld, world_type):
    worlds = [multiworld.worlds[p] for p in multiworld.player_ids
              if isinstance(multiworld.worlds[p], world_type)
              and not getattr(multiworld.worlds[p], "_ammo_finalized", False)]
    if not worlds:
        return
    # get_spheres yields an empty sentinel followed by UNREACHABLE locations.
    # Never rank that final bucket as an obtainable weapon.
    spheres = {}
    for index, sphere in enumerate(multiworld.get_spheres(), start=1):
        if not sphere:
            break
        spheres.update((location, index) for location in sphere)
    all_locations = list(multiworld.get_filled_locations())
    ammo_names = {ammo for _, ammo in AMMO_WEAPON_PAIRS}
    gun_names = {gun for gun, _ in AMMO_WEAPON_PAIRS}
    replacements = {}
    for world in worlds:
        player = world.player
        recipients = {player} | {group_id for group_id, group in multiworld.groups.items()
                                  if player in group["players"]}
        first = {item.name: 0 for owner in recipients
                 for item in multiworld.precollected_items.get(owner, []) if item.name in gun_names}
        for loc, sphere in spheres.items():
            item = loc.item
            if item.player in recipients and item.name in gun_names:
                first[item.name] = min(first.get(item.name, sphere), sphere)
        ranked = sorted(first)
        world.random.shuffle(ranked)  # seeded, unbiased tie break for the same sphere
        ranked.sort(key=first.get)
        locations = sorted((loc for loc in all_locations
                            if loc.item.player == player and loc.item.name in ammo_names
                            and loc.item.classification == ItemClassification.filler
                            and not loc.locked and loc.address is not None),
                           key=lambda loc: (loc.player, loc.name))
        world.random.shuffle(locations)
        counts = allocate(len(locations), ranked)
        rewards = match_rewards(world, locations, counts) if ranked else None
        status = "applied" if rewards is not None else (
            "unchanged_no_reachable_gun" if not ranked else "unchanged_placement_constraints")
        if rewards is not None:
            for loc, name in zip(locations, rewards):
                old = loc.item
                item = world.create_item(name)
                loc.item = item
                item.location = loc
                old.location = None
                replacements[id(old)] = item
        world.ammo_distribution = {
            "status": status,
            "weapon_order": ranked,
            "weapon_spheres": first,
            "vanilla_pickup_counts": dict(AMMO_VANILLA_COUNTS),
            "adjustable_ammo_count": len(locations),
            "target_counts": counts,
            "final_counts": dict(Counter(loc.item.name for loc in all_locations
                                         if loc.item.player == player and loc.item.name in ammo_names)),
        }
        world._ammo_finalized = True
    # Keep both AP's placement graph and its item pool consistent by identity;
    # Item equality deliberately treats different copies of one ammo as equal.
    multiworld.itempool[:] = [replacements.get(id(item), item) for item in multiworld.itempool]
