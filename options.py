from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions, Toggle, Range, DeathLink, OptionSet, OptionError


class Goal(Choice):
    """Kill God: finish by defeating God.
    Kill All Bosses: defeat Split Worm, Missionary, Leonard, Memory of Alessa and God.
    Each boss awards a check in either mode.
    """
    display_name = "Goal"
    option_kill_god = 0
    option_kill_all_bosses = 1
    default = 0


class FastTravelUnlocks(Choice):
    """Vanilla: each save-point check awards its own travel unlock locally.
    Randomized: named travel unlocks can be placed anywhere in the multiworld.
    Starting: begin with every travel destination unlocked.
    Random Starting Area always forces Randomized, overriding this selection.
    Interacting with a save point also permanently unlocks its destination in
    every mode, without granting that check's shuffled reward a second time.
    Teleports bypass earlier route requirements, but local locks retain theirs.
    Save points remain checks; opening the save screen is enough.
    """
    display_name = "Fast Travel Unlocks"
    option_vanilla = 0
    option_randomized = 1
    alias_anywhere = 1
    option_starting = 3
    default = 0

    @classmethod
    def from_any(cls, value):
        if (isinstance(value, str) and value.strip().casefold() == "progressive") or value == 2:
            raise OptionError("Invalid Fast Travel Unlocks value. Use vanilla, randomized, or starting.")
        return super().from_any(value)


class MapLocations(Choice):
    """Starting: begin with all seven maps already owned.
    Vanilla: each map stays at its original map check.
    Anywhere: maps can be placed anywhere in the multiworld.
    Map pickups remain checks in every mode.
    """
    display_name = "Map Locations"
    option_starting = 0
    option_vanilla = 1
    option_anywhere = 2
    default = 0


class AddCostumesToItemPool(Toggle):
    """Add all 12 costumes, including Transform Costume, to the item pool.
    Costumes replace consumable filler and may be placed in other games.
    """
    display_name = "Add Costumes to Item Pool"
    default = 1


class SingleShakespeareAnthology(Toggle):
    """One Shakespeare Anthology reward grants all five books together.
    The other four book rewards become supplies. All pickup checks remain.
    """
    display_name = "Single Shakespeare Anthology"
    default = 0


class SingleTarotCard(Toggle):
    """One Tarot Cards reward grants all five cards together.
    The other four card rewards become supplies. All pickup checks remain.
    """
    display_name = "Single Tarot Card"
    default = 0


class RandomStartingArea(Toggle):
    """Begin a New Game at one of the 29 seeded save points. This forces
    Fast Travel Unlocks to Randomized, regardless of the selected travel mode.
    Only the chosen starting save is granted: Mall Toilet is NOT a free return.
    The three Starting Item checks are in logic regardless of the chosen save.
    Connect before New Game. Continue and loading a save retain their position.
    """
    display_name = "Random Starting Area"
    default = 0


class StartingKnife(Toggle):
    """Start with the Knife. Its item-pool slot becomes consumable filler."""
    display_name = "Starting Knife"
    default = 0


class StartingHandgun(Toggle):
    """Start with the Handgun. Its item-pool slot becomes consumable filler."""
    display_name = "Starting Handgun"
    default = 0


class StartingFlashlight(Toggle):
    """Start with the Flashlight. Its item-pool slot becomes consumable filler."""
    display_name = "Starting Flashlight"
    default = 0


class StartingRadio(Toggle):
    """Start with the Radio. Its item-pool slot becomes consumable filler."""
    display_name = "Starting Radio"
    default = 0


EXTRA_NEW_GAME_ITEMS = {
    "Unlimited Submachine Gun": ("Unlimited Submachine Gun",),
    "Beam Saber": ("Beam Saber",),
    "Flamethrower": ("Flamethrower",),
    "Gold and Silver Pipes": ("Gold Pipe", "Silver Pipe"),
    "Heather Beam": ("Heather Beam",),
}


class IncludedExtraNewGameItems(OptionSet):
    """Extra New Game rewards included in the item pool. Remove an entry to
    exclude that reward and replace its slot with consumable filler.
    Gold and Silver Pipes are one entry and are included or excluded together.
    Heather Beam unlocks the ability; the UFO ending remains disabled.
    """
    display_name = "Included Extra New Game Items"
    valid_keys = frozenset(EXTRA_NEW_GAME_ITEMS)
    default = frozenset(EXTRA_NEW_GAME_ITEMS)


class AmmoWeight(Range):
    """Relative ammunition frequency compared with healing supplies.
    Raise for more ammo or lower for less. Equal ammo and healing weights
    preserve the existing mix. Only consumable filler rewards change.
    Ammunition is still distributed toward weapons found earlier in the seed.
    """
    display_name = "Ammo Weight"
    range_start = 25
    range_end = 200
    default = 100


class HealingWeight(Range):
    """Relative Health Drink, First-Aid Kit and Ampoule frequency.
    Raise for more healing or lower for less. Equal ammo and healing weights
    preserve the existing mix. Changes rewards, not healing strength.
    """
    display_name = "Healing Weight"
    range_start = 25
    range_end = 200
    default = 100


class TrapPercentage(Range):
    """Percentage of consumable filler replaced by traps. Zero disables traps.
    Progression and useful items are never replaced.
    """
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0


class IncludedTraps(OptionSet):
    """Remove entries to exclude individual traps.
    Damage: non-lethal health loss. Stumble: a single hit reaction without damage.
    Exhaustion: temporary maximum fatigue. Blackout: temporary flashlight loss.
    Radio Static: false enemy static. False Alarm: a brief scare sound.
    """
    display_name = "Included Traps"
    valid_keys = frozenset(("Damage", "Stumble", "Exhaustion", "Blackout", "Radio Static", "False Alarm"))
    default = valid_keys


class TrapIntensity(Choice):
    """Mild / Normal / Severe: Damage removes 10 / 20 / 30 percent of maximum
    health, never reducing health below 1. Exhaustion, Blackout and Radio Static
    last 5 / 10 / 15 seconds of active gameplay. Stumble and False Alarm happen
    once. Traps apply one at a time, with a short gap between effects.
    """
    display_name = "Trap Intensity"
    option_mild = 0
    option_normal = 1
    option_severe = 2
    default = 1


@dataclass
class SilentHill3Options(PerGameCommonOptions):
    goal: Goal
    fast_travel_unlocks: FastTravelUnlocks
    map_locations: MapLocations
    add_costumes_to_item_pool: AddCostumesToItemPool
    included_extra_new_game_items: IncludedExtraNewGameItems
    single_shakespeare_anthology: SingleShakespeareAnthology
    single_tarot_card: SingleTarotCard
    random_starting_area: RandomStartingArea
    starting_knife: StartingKnife
    starting_handgun: StartingHandgun
    starting_flashlight: StartingFlashlight
    starting_radio: StartingRadio
    ammo_weight: AmmoWeight
    healing_weight: HealingWeight
    death_link: DeathLink
    trap_percentage: TrapPercentage
    included_traps: IncludedTraps
    trap_intensity: TrapIntensity
