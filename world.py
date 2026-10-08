from collections import Counter
from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from .data import (
    ACTIVE_LOCATION_NAME_TO_ID,
    active_locations, SCRIPTED_PROTOCOL, SCRIPTED_CHECKS, SCRIPTED_LOCATION_NAMES,
    MALL_ADDED_POOL_ITEMS, MALL_MAP_ITEM, MALL_MAP_LOCATION, BOSS_LOCATION,
    MAP_CHECK_ITEMS, POST_MALL_ADDED_POOL_ITEMS, VERIFIED_ADDED_POOL_ITEMS,
    SUPPORTED_BOSS_LOCATIONS, BOSS_WEAPONS, BOSS_WEAPON_COMBINATIONS, boss_checks_enabled,
    BOSS_EVENT_ITEMS, ITEM_TALISMAN, SILENCER_LOCATION, SILENCER_WEAPONS,
    ITEM_SUBMACHINE_GUN, ITEM_SUBMACHINE_GUN_BULLETS, AMMO_WEAPON_PAIRS, AMMO_VANILLA_COUNTS,
    ACTIVE_FAST_TRAVEL_ROWS, FAST_TRAVEL_MENU_LOCATIONS, SAVE_LOCATION_NAMES,
    SAVE_ID_TO_LOCATION_ID, SAVE_TRAVEL_PROTOCOL, ITEM_PROGRESSIVE_FAST_TRAVEL,
    CATALOGUE_VERSION,
    COSTUME_RAW_IDS,
    GAME_NAME,
    ITEM_HEATHER_BEAM,
    ITEM_BEAM_SABER,
    ITEM_BEEF_JERKY,
    ITEM_CLASSIFICATION,
    ITEM_FIRST_AID_KIT,
    ITEM_FLASHLIGHT,
    ITEM_FLAMETHROWER,
    ITEM_GOLD_PIPE,
    ITEM_HANDGUN,
    ITEM_HANDGUN_BULLETS,
    ITEM_HEALTH_DRINK,
    ITEM_HOUSE_KEY,
    ITEM_ID_TO_RAW,
    ITEM_KATANA,
    ITEM_KEY_TAKEN_WITH_TONGS,
    ITEM_KNIFE,
    ITEM_MATCHBOOK,
    ITEM_NAME_TO_ID,
    ITEM_OXYDOL,
    ITEM_PENDANT,
    ITEM_PORK_LIVER,
    ITEM_RADIO,
    ITEM_SHOTGUN,
    ITEM_SHOTGUN_SHELLS,
    ITEM_SILVER_PIPE,
    ITEM_STEEL_PIPE,
    ITEM_STUN_GUN,
    ITEM_STUN_GUN_BATTERY,
    ITEM_TONGS,
    ITEM_UNLIMITED_SUBMACHINE_GUN,
    LOCATION_NAME_TO_ID,
    PERSIST_FLAG_TO_LOCATION_ID,
    PROTOCOL_VERSION,
    START_LOCATION_NAMES,
    WORLD_VERSION,
)
from .options import SilentHill3Options, EXTRA_NEW_GAME_ITEMS
from Options import OptionGroup, CommonOptions
from .ammo import rebalance_ammo
from .supplies import balance_supplies
from .traps import replace_filler_with_traps
from .data import TRAP_ITEM_IDS, BUNDLED_ITEMS
from .travel_logic import (can_access as travel_access, state_owned, FLASHLIGHT_CHECKS,
                           starting_roots, VISIT_EVENT_ITEMS, save_events_settled, LOGIC_VERSION)


def can_access_silencer_wall(state, player):
    """Local requirement, in addition to reaching the Construction Site."""
    return (state.has(ITEM_FLASHLIGHT, player)
            and any(state.has(weapon, player) for weapon in SILENCER_WEAPONS))


class SilentHill3Item(Item):
    game = GAME_NAME


class SilentHill3Location(Location):
    game = GAME_NAME


class SilentHill3WebWorld(WebWorld):
    option_groups = [
        OptionGroup("Game Options", [SilentHill3Options.type_hints[name]
            for name in SilentHill3Options.__annotations__ if name not in ("trap_percentage", "included_traps", "trap_intensity")]),
        OptionGroup("Traps", [SilentHill3Options.type_hints[name] for name in ("trap_percentage", "included_traps", "trap_intensity")]),
        OptionGroup("Item & Location Options", list(CommonOptions.type_hints.values()), True),
    ]
    theme = "dirt"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "Silent Hill 3 Archipelago setup.",
        "English",
        "setup_en.md",
        "setup/en",
        ["SH3AP"],
    )
    tutorials = [setup_en]


class SilentHill3World(World):
    game = GAME_NAME
    web = SilentHill3WebWorld()
    options_dataclass = SilentHill3Options
    options: SilentHill3Options
    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups = {
        "Traps": {name + " Trap" for name in TRAP_ITEM_IDS.values()},
        "Ammo": {ammo for _, ammo in AMMO_WEAPON_PAIRS},
        "Boss Weapons": set(BOSS_WEAPONS),
        "Fast Travel": set(SAVE_LOCATION_NAMES),
        "Costumes": set(COSTUME_RAW_IDS),
        "Supplies": {
            ITEM_HEALTH_DRINK,
            ITEM_FIRST_AID_KIT,
            ITEM_HANDGUN_BULLETS,
            ITEM_SHOTGUN_SHELLS,
            ITEM_BEEF_JERKY,
            ITEM_STUN_GUN_BATTERY,
            ITEM_SUBMACHINE_GUN_BULLETS,
            "Ampoule",
        },
        "Current Progression": {
            ITEM_FLASHLIGHT,
            ITEM_TONGS,
            ITEM_KEY_TAKEN_WITH_TONGS,
            ITEM_OXYDOL,
            ITEM_PORK_LIVER,
            ITEM_MATCHBOOK,
            ITEM_PENDANT,
            ITEM_HOUSE_KEY,
        },
        "Weapons": {
            ITEM_KNIFE,
            ITEM_HANDGUN,
            ITEM_SHOTGUN,
            ITEM_STEEL_PIPE,
            ITEM_KATANA,
            ITEM_STUN_GUN,
            ITEM_UNLIMITED_SUBMACHINE_GUN,
            ITEM_BEAM_SABER,
            ITEM_FLAMETHROWER,
            ITEM_GOLD_PIPE,
            ITEM_SILVER_PIPE,
            ITEM_SUBMACHINE_GUN,
            "Maul",
        },
    }
    location_name_groups = {
        "All Checks": set(ACTIVE_LOCATION_NAME_TO_ID),
    }
    required_client_version = (0, 6, 7)
    origin_region_name = "Silent Hill 3 Ready Checks"

    # Base pool for inventory-backed rewards; special game-state rewards are
    # added separately by their dedicated generation paths.
    BASE_ITEM_POOL = [
        # Restore the original pool and its three unrestricted start checks.
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        # Progression (8)
        ITEM_FLASHLIGHT,
        ITEM_TONGS,
        ITEM_KEY_TAKEN_WITH_TONGS,
        ITEM_OXYDOL,
        ITEM_PORK_LIVER,
        ITEM_MATCHBOOK,
        ITEM_PENDANT,
        ITEM_HOUSE_KEY,
        # Weapons: eligible boss weapons are progression; Knife/Stun Gun are useful.
        ITEM_KNIFE,
        ITEM_HANDGUN,
        ITEM_SHOTGUN,
        ITEM_STEEL_PIPE,
        ITEM_KATANA,
        ITEM_STUN_GUN,
        ITEM_UNLIMITED_SUBMACHINE_GUN,
        ITEM_BEAM_SABER,
        ITEM_FLAMETHROWER,
        ITEM_GOLD_PIPE,
        ITEM_SILVER_PIPE,
        # Filler (19)
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_HEALTH_DRINK,
        ITEM_FIRST_AID_KIT,
        ITEM_FIRST_AID_KIT,
        ITEM_FIRST_AID_KIT,
        ITEM_FIRST_AID_KIT,
        ITEM_HANDGUN_BULLETS,
        ITEM_HANDGUN_BULLETS,
        ITEM_HANDGUN_BULLETS,
        ITEM_HANDGUN_BULLETS,
        ITEM_SHOTGUN_SHELLS,
        ITEM_SHOTGUN_SHELLS,
        ITEM_BEEF_JERKY,
        ITEM_STUN_GUN_BATTERY,
        ITEM_RADIO,
    ]

    def generate_early(self):
        # Enforce the dependency here, not merely in a sample YAML/UI.
        if self.options.random_starting_area.value:
            self.options.fast_travel_unlocks.value = 1
        elif self.options.fast_travel_unlocks.value not in (0, 1, 3):
            raise ValueError("Invalid Fast Travel Unlocks value; select vanilla, randomized, or starting.")
        self.starting_area_row = (self.random.choice(ACTIVE_FAST_TRAVEL_ROWS)
                                  if self.options.random_starting_area.value else None)

    def collect(self, state, item):
        changed = super().collect(state, item)
        if item.name in BUNDLED_ITEMS:
            for member in BUNDLED_ITEMS[item.name]:
                state.prog_items[self.player][member] += 1
            return True
        return changed

    def remove(self, state, item):
        changed = super().remove(state, item)
        if changed and item.name in BUNDLED_ITEMS:
            for member in BUNDLED_ITEMS[item.name]:
                state.prog_items[self.player][member] -= 1
                if not state.prog_items[self.player][member]:
                    del state.prog_items[self.player][member]
        return changed

    def boss_checks_enabled(self):
        return boss_checks_enabled(self.options.goal.current_key, False)

    def current_locations(self):
        return active_locations(self.boss_checks_enabled())

    def create_regions(self) -> None:
        if not hasattr(self, "starting_area_row"):
            self.generate_early()
        region = Region(self.origin_region_name, self.player, self.multiworld)
        for name, address in self.current_locations().items():
            region.locations.append(SilentHill3Location(self.player, name, address, region))
        # Actual save interaction permanently unlocks the destination, even if
        # its randomized network reward is unrelated. Addressless visit events
        # model that mechanic without adding checks or changing the item pool.
        for row, item_name in VISIT_EVENT_ITEMS.items():
            event = SilentHill3Location(self.player, item_name, None, region)
            event.place_locked_item(SilentHill3Item(item_name, ItemClassification.progression, None, self.player))
            region.locations.append(event)
        # Addressless progression events express the goal in generation logic;
        # they do not add network checks or consume random item-pool slots.
        for boss, item_name in BOSS_EVENT_ITEMS.items():
            event = SilentHill3Location(self.player, "Defeat " + boss, None, region)
            event.place_locked_item(SilentHill3Item(item_name, ItemClassification.progression, None, self.player))
            region.locations.append(event)
        self.multiworld.regions.append(region)

    def _duplicate_filler(self, pool: list[str]) -> str:
        # Duplicate an existing consumable, weighted by its current abundance.
        # Do not put an enabled starting Radio or a unique costume back in the pool.
        candidates = [name for name in pool if name in self.item_name_groups["Supplies"]
                      and ITEM_CLASSIFICATION[name] == "filler"]
        if not candidates:
            raise RuntimeError("No existing consumable filler is available to duplicate")
        return self.random.choice(candidates)

    def _replace_pool_item_with_filler(self, pool: list[str], name: str) -> None:
        if name in pool:
            pool.remove(name)
            pool.append(self._duplicate_filler(pool))

    def _precollect_and_replace(self, pool: list[str], name: str) -> None:
        if name in pool:
            pool.remove(name)
            self.multiworld.push_precollected(self.create_item(name))
            pool.append(self._duplicate_filler(pool))

    def _add_items_by_filler_ratio(self, pool: list[str], additions: list[str]) -> None:
        """Replace the three most common filler types using largest remainders.

        Count before adding the new items. Alphabetical order breaks equal
        counts/remainders so the result is reproducible for a given seed.
        """
        counts = Counter(name for name in pool if ITEM_CLASSIFICATION[name] == "filler")
        top = sorted(counts, key=lambda name: (-counts[name], name))[:3]
        total = sum(counts[name] for name in top)
        needed = len(additions)
        if total < needed:
            raise RuntimeError("Not enough filler among the three most common types for added items")
        if not needed:
            return
        allocation = {name: needed * counts[name] // total for name in top}
        remainder_order = sorted(top, key=lambda name: (-(needed * counts[name] % total), name))
        for name in remainder_order[:needed - sum(allocation.values())]:
            allocation[name] += 1
        for name, count in allocation.items():
            for _ in range(count):
                pool.remove(name)
        pool.extend(additions)

    def create_items(self) -> None:
        pool = list(self.BASE_ITEM_POOL)
        # Newly mapped checklist locations add slots. Fill them with seeded
        # duplicates of supported consumables before optional replacements.
        # A boss adds exactly one supply beyond the same non-boss pool. Append
        # it after all replacements so a new costume/key cannot consume it.
        boss_count = sum(name in self.current_locations() for name in SUPPORTED_BOSS_LOCATIONS)
        while len(pool) < len(self.current_locations()) - boss_count:
            pool.append(self._duplicate_filler(pool))

        self._add_items_by_filler_ratio(pool, list(MALL_ADDED_POOL_ITEMS))
        self._add_items_by_filler_ratio(pool, list(POST_MALL_ADDED_POOL_ITEMS))
        self._add_items_by_filler_ratio(pool, list(VERIFIED_ADDED_POOL_ITEMS))
        self._add_items_by_filler_ratio(pool, [ITEM_SUBMACHINE_GUN, ITEM_TALISMAN, ITEM_HEATHER_BEAM])

        for enabled, bundle in (
            (self.options.single_shakespeare_anthology.value, "Shakespeare Anthology"),
            (self.options.single_tarot_card.value, "Tarot Cards"),
        ):
            if enabled:
                members = BUNDLED_ITEMS[bundle]
                for name in members:
                    pool.remove(name)
                pool.append(bundle)
                pool.extend(self._duplicate_filler(pool) for _ in members[1:])

        for entry, items in EXTRA_NEW_GAME_ITEMS.items():
            if entry not in self.options.included_extra_new_game_items.value:
                for name in items:
                    self._replace_pool_item_with_filler(pool, name)

        for option, name in (
            (self.options.starting_knife, ITEM_KNIFE),
            (self.options.starting_flashlight, ITEM_FLASHLIGHT),
            (self.options.starting_handgun, ITEM_HANDGUN),
            (self.options.starting_radio, ITEM_RADIO),
        ):
            if option.value:
                self._precollect_and_replace(pool, name)

        if self.options.add_costumes_to_item_pool.value:
            self._add_items_by_filler_ratio(pool, list(COSTUME_RAW_IDS))

        travel_items = list(SAVE_LOCATION_NAMES)
        self._add_items_by_filler_ratio(pool, travel_items)
        locked_count = 0
        if self.options.map_locations.current_key == "vanilla":
            for location_name, item_name in MAP_CHECK_ITEMS.items():
                self.multiworld.get_location(location_name, self.player).place_locked_item(self.create_item(item_name))
                pool.remove(item_name)
                locked_count += 1
        if self.options.fast_travel_unlocks.current_key == "vanilla":
            # OFF still creates each visited-save check; its reward stays local.
            for location_name, item_name in zip(SAVE_LOCATION_NAMES, travel_items):
                self.multiworld.get_location(location_name, self.player).place_locked_item(self.create_item(item_name))
                pool.remove(item_name)
                locked_count += 1

        if self.options.map_locations.current_key == "starting":
            for name in MAP_CHECK_ITEMS.values():
                self._precollect_and_replace(pool, name)
        if self.options.fast_travel_unlocks.current_key == "starting":
            for name in SAVE_LOCATION_NAMES:
                self._precollect_and_replace(pool, name)

        if self.starting_area_row is not None:
            # Only the real start is guaranteed. Its one pool copy becomes
            # consumable filler; no duplicate reward or free Mall return is added.
            self._precollect_and_replace(pool, FAST_TRAVEL_MENU_LOCATIONS[self.starting_area_row])

        for _ in range(boss_count):
            pool.append(self._duplicate_filler(pool))

        pool, self.supply_distribution = balance_supplies(
            pool, self.options.ammo_weight.value, self.options.healing_weight.value)

        pool = replace_filler_with_traps(pool, self.options.trap_percentage.value,
                                        self.options.included_traps.value, self.random)

        if len(pool) + locked_count != len(self.current_locations()):
            raise RuntimeError(
                f"SH3 item pool/location mismatch: {len(pool)} items for "
                f"{len(self.current_locations())} locations"
            )

        self.multiworld.itempool += [self.create_item(name) for name in pool]

    def create_item(self, name: str) -> SilentHill3Item:
        class_name = ITEM_CLASSIFICATION[name]
        # Knife opens the hidden Silencer wall, so it participates in logic.
        if name == ITEM_KNIFE and SILENCER_LOCATION in self.current_locations():
            class_name = "progression"
        classification = {
            "progression": ItemClassification.progression,
            "useful": ItemClassification.useful,
            "filler": ItemClassification.filler,
            "trap": ItemClassification.trap,
        }[class_name]
        return SilentHill3Item(name, classification, self.item_name_to_id[name], self.player)

    def get_filler_item_name(self) -> str:
        return ITEM_HEALTH_DRINK

    @classmethod
    def stage_pre_output(cls, multiworld):
        # All fill, progression balancing and finalize hooks are finished.
        # Only non-progression ammo identities change; no logical spheres move.
        rebalance_ammo(multiworld, cls)
        # Validate every retained spoiler step when testing item removals; the
        # permanent Hospital transition makes goal-only pruning insufficient.
        from .spoiler_safety import install_spoiler_safety
        install_spoiler_safety(multiworld)

    def write_spoiler(self, spoiler_handle):
        info = getattr(self, "ammo_distribution", None)
        if info:
            spoiler_handle.write(f"\nSH3 ammo distribution ({self.multiworld.player_name[self.player]}):\n")
            spoiler_handle.write("Weapon order: " + ", ".join(info["weapon_order"]) + "\n")
            spoiler_handle.write("Policy: retained Normal checklist ratio 31:10:3, earliest gun first.\n")
            for name, count in sorted(info["final_counts"].items()):
                spoiler_handle.write(f"  {name}: {count}\n")
            spoiler_handle.write("Status: " + info["status"] + "\n")

    def set_rules(self) -> None:
        roots = starting_roots(self.starting_area_row)
        for name in self.current_locations():
            self.multiworld.get_location(name, self.player).access_rule = (
                lambda state, name=name: travel_access(name, state_owned(state, self.player), roots))
        for row, event_name in VISIT_EVENT_ITEMS.items():
            self.multiworld.get_location(event_name, self.player).access_rule = (
                lambda state, row=row: travel_access(FAST_TRAVEL_MENU_LOCATIONS[row], state_owned(state, self.player), roots))
        for boss in BOSS_EVENT_ITEMS:
            # A same-sphere boss event must not erase a save that was reachable
            # before its irreversible transition. Sweep visit-unlock bookkeeping
            # first; no extra network checks or progression items are required.
            self.multiworld.get_location("Defeat " + boss, self.player).access_rule = (
                lambda state, name=boss: travel_access(name, state_owned(state, self.player), roots)
                and (name != "Leonard" or save_events_settled(state, self.player, roots)))
        required = ((BOSS_EVENT_ITEMS["God"],) if self.options.goal.current_key == "kill_god"
                    else tuple(BOSS_EVENT_ITEMS.values()))
        self.multiworld.completion_condition[self.player] = lambda state: all(state.has(n, self.player) for n in required)

    def fill_slot_data(self) -> dict:
        return {
            "goal": self.options.goal.current_key,
            "single_shakespeare_anthology": bool(self.options.single_shakespeare_anthology.value),
            "single_tarot_card": bool(self.options.single_tarot_card.value),
            "random_starting_area": bool(self.options.random_starting_area.value),
            "starting_area_row": self.starting_area_row,
            "starting_area_name": (FAST_TRAVEL_MENU_LOCATIONS[self.starting_area_row]
                                   if self.starting_area_row is not None else 'Mall 1F Toilet Fast Travel'),
            "bundle_receive_protocol": 1,
            "random_start_protocol": 1,
            "fast_travel_unlocks": self.options.fast_travel_unlocks.current_key,
            "map_locations": self.options.map_locations.current_key,
            "included_extra_new_game_items": sorted(self.options.included_extra_new_game_items.value),
            "sh3ap_world_version": WORLD_VERSION,
            "trap_protocol": 1,
            "trap_percentage": self.options.trap_percentage.value,
            "included_traps": sorted(self.options.included_traps.value),
            "trap_intensity": self.options.trap_intensity.value,
            "sh3ap_catalogue_version": CATALOGUE_VERSION,
            "sh3ap_pipe_protocol": PROTOCOL_VERSION,
            "gathered_check_count": len(LOCATION_NAME_TO_ID),
            "active_location_count": len(self.current_locations()),
            "save_travel_protocol": SAVE_TRAVEL_PROTOCOL,
            "confirmed_save_ids": sorted(SAVE_ID_TO_LOCATION_ID),
            "fast_travel_rows": list(ACTIVE_FAST_TRAVEL_ROWS),
            "fast_travel_item_count": len(SAVE_LOCATION_NAMES),
            "fast_travel_unlock_on_visit": True,
            "fast_travel_logic_version": LOGIC_VERSION,
            "random_start_forces_randomized_fast_travel": True,
            "starting_checks_independent_of_start_region": True,
            "hospital_post_leonard_lobby_only": True,
            "fast_travel_implementation_scope": "all 29 save openings verified from recorded interactions",
            "save_check_policy": "open_save_screen_once_per_seed_team_slot; no_save_required",
            "randomized_item_pool_count": len(self.current_locations()) - (len(SAVE_LOCATION_NAMES) if self.options.fast_travel_unlocks.current_key == "vanilla" else 0) - (len(MAP_CHECK_ITEMS) if self.options.map_locations.current_key == "vanilla" else 0),
            "scripted_check_protocol": SCRIPTED_PROTOCOL,
            "scripted_location_ids": sorted(LOCATION_NAME_TO_ID[name] for name in SCRIPTED_LOCATION_NAMES
                                            if name in self.current_locations()),
            "scripted_check_scope": "Verified scripted pickups through Amusement Park and Church; seven maps; all five bosses",
            "confirmed_location_flags": sorted(PERSIST_FLAG_TO_LOCATION_ID),
            "physical_supply_slots": [1011, 1012, 1026, 1027, 1030],
            "supply_contents_may_vary": True,
            "server_item_delivery_enabled": True,
            "direct_persistent_flag_reader": False,
            "location_completion_policy": "live_events_only",
            "save_load_location_recovery_enabled": False,
            "real_item_pool_implemented": True,
            "heather_beam_reward_implemented": True,
            "real_item_pool_count": len(self.current_locations()),
            "normal_inventory_receive_mappings": len(ITEM_ID_TO_RAW),
            "current_item_classifications_implemented": True,
            "current_access_rules_implemented": True,
            "current_access_rule_scope": "directional save-entry routes, exhaustive backward limits, local item gates, and the permanent post-Leonard Hospital barrier",
            "starting_item_catalogue_runtime_ids_updated": True,
            "add_costumes_to_item_pool": bool(self.options.add_costumes_to_item_pool.value),
            "add_costumes_to_item_pool_implemented": True,
            "costume_item_count_when_implemented": 12,
            "include_unlimited_submachine_gun": ("Unlimited Submachine Gun" in self.options.included_extra_new_game_items.value),
            "include_beam_saber": ("Beam Saber" in self.options.included_extra_new_game_items.value),
            "include_flamethrower": ("Flamethrower" in self.options.included_extra_new_game_items.value),
            "include_gold_pipe": ("Gold and Silver Pipes" in self.options.included_extra_new_game_items.value),
            "include_silver_pipe": ("Gold and Silver Pipes" in self.options.included_extra_new_game_items.value),
            "include_heather_beam": ("Heather Beam" in self.options.included_extra_new_game_items.value),
            "extra_new_game_item_options_implemented": True,
            "include_fast_travel_points": (self.options.fast_travel_unlocks.current_key != "vanilla"),
            "include_fast_travel_points_implemented": True,
            "win_condition": self.options.goal.current_key,
            "win_condition_default": "kill_god",
            "boss_goal_reporting_implemented": True,
            "randomize_maps": (self.options.map_locations.current_key != "vanilla"),
            "randomize_maps_implemented": True,
            "randomize_maps_scope": "Mall, Subway, Underpass, Office, Silent Hill, Hospital and Church maps",
            "randomize_boss_checks": self.boss_checks_enabled(),
            "boss_check_locations": list(SUPPORTED_BOSS_LOCATIONS) if self.boss_checks_enabled() else [],
            "boss_supply_filler_count": len(SUPPORTED_BOSS_LOCATIONS) if self.boss_checks_enabled() else 0,
            "boss_required_weapons": sorted(BOSS_WEAPONS),
            "boss_weapon_combinations": [list(combo) for combo in BOSS_WEAPON_COMBINATIONS],
            "ammo_weight": self.options.ammo_weight.value,
            "healing_weight": self.options.healing_weight.value,
            "supply_distribution": getattr(self, "supply_distribution", {}),
            "death_link": bool(self.options.death_link.value),
            "ammo_distribution": getattr(self, "ammo_distribution", {"status": "pending_fill"}),
            "ammo_distribution_policy": "normal_checklist_ratio_ranked_by_final_weapon_sphere",
            "randomize_boss_checks_implemented": True,
            "randomize_boss_checks_scope": "all five bosses; live defeats persisted per AP seed/team/slot",
            "legacy_starting_item_options_ignored": False,
            "starting_item_options_implemented": True,
            "starting_handgun_runtime_supported": True,
            "pool_addition_replacement_policy": "top_three_filler_proportional_largest_remainder",
            "removed_item_replacement_policy": "seeded_random_existing_consumable_duplicate",
            "automatic_start_checks": list(START_LOCATION_NAMES),
            "automatic_start_checks_unrestricted": True,
            "new_game_inventory_cleanup": True,
            "progressive_fast_travel": False,
            "progressive_fast_travel_implemented": False,
        }
