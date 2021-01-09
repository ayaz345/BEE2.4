"""The different properties defineable for items."""
from typing import Type, TypeVar, Generic, ClassVar, Sequence, Dict
from abc import abstractmethod
from enum import Enum
from srctools import Property as KeyValues  # Prevent confusion
from srctools import conv_bool, conv_int, conv_float, bool_as_int, Angle


ValueT = TypeVar('ValueT')


class ItemProp(Generic[ValueT]):
    """A property for an item."""
    id: ClassVar[str]  # Property name for this.
    trans_name: ClassVar[str]  # The translation keyword for this, if it exists.
    instvar: ClassVar[str]  # The instance variable this sets, if any.
    # All the possible values this can have, if used as a subtype.
    # If not useable, produce a zero-length sequence.
    subtype_values: ClassVar[Sequence[ValueT]] = ()

    def __init__(self, default: ValueT) -> None:
        self.default = default

    def __repr__(self) -> str:
        """Generic repr() for properties."""
        return f'{type(self).__qualname__}({self.default!r})'

    def __eq__(self, other):
        """Subclasses do not compare equal."""
        if type(self) is type(other):
            return self.default == other.default
        return NotImplemented

    def __ne__(self, other):
        """Subclasses do not compare equal."""
        if type(self) is type(other):
            return self.default != other.default
        return NotImplemented

    @staticmethod
    def parse(props: KeyValues) -> 'ItemProp':
        """Parse a property block, picking the appropriate class."""
        cls = PROP_TYPES[props.name]

        return cls(cls._parse_value(props['DefaultValue', '']))

    def export(self, index: int = 0) -> KeyValues:
        """Generate the property block to write this back to the file.

        A unique index must be provided if the variable produces an instvar.
        """
        if self.instvar:
            if index <= 0:
                raise ValueError(
                    type(self).__qualname__ + '() requires an index!')
        else:
            index = 0
        return KeyValues(self.id, [
            KeyValues('DefaultValue', self._export_value(self.default)),
            KeyValues('Index', str(index)),
        ])

    # Subclasses should implement the following:

    @staticmethod
    @abstractmethod
    def _parse_value(value: str) -> ValueT:
        raise NotImplementedError

    @staticmethod
    def _export_value(value: ValueT) -> str:
        return str(value)


# ID -> class
PROP_TYPES: Dict[str, Type[ItemProp]] = {}


class _BoolProp(ItemProp[bool]):
    """Implements boolean-type properties."""
    subtype_values = (False, True)

    @staticmethod
    def _parse_value(value: str) -> bool:
        return conv_bool(value)

    @staticmethod
    def _export_value(value: bool) -> str:
        return bool_as_int(value)


class _FloatProp(ItemProp[float]):
    """Implements float-type properties. These are all internal."""
    trans_name = ''  # Hidden prop

    @staticmethod
    def _parse_value(value: str) -> float:
        return conv_float(value)


class _EnumProp(ItemProp[ValueT], Generic[ValueT]):
    """*Type props, with an enum."""
    _enum: ClassVar[Type[ValueT]]

    @classmethod
    def _parse_value(cls, value: str) -> ValueT:
        try:
            return cls._enum[value.upper()]
        except ValueError:
            pass
        return cls._enum(int(value))

    @staticmethod
    def _export_value(typ: ValueT) -> str:
        return str(typ.value)

# Enumerations for various types.


class PanelAnimation(Enum):
    """Available angles for angled panels."""
    ANGLE_30 = 30
    ANGLE_45 = 45
    ANGLE_60 = 60
    AMGLE_90 = 90


class PanelType(Enum):
    """The type of angled panel that is used."""
    ANGLED = '0'
    GLASS = '1'


class PaintTypes(Enum):
    """The 5 types of gel that exist."""
    BLUE = BOUNCE = "bounce"
    ORAN = ORANGE = SPEED = "speed"
    WHITE = PORTAL = "portal"
    WATER = CLEANSING = ERASE = "erase"
    GREY = GRAY = REFLECT = "reflect"  # Extra/hacked in.


class PaintFlows(Enum):
    """The different flow amounts paint can have."""
    LIGHT = 'light'
    MEDIUM = 'medium'
    HEAVY = 'heavy'
    DRIP = 'drip'
    BOMB = 'bomb'


class CubeTypes(Enum):
    """The different types of cubes."""
    STANDARD = 0
    COMPANION = 1
    REFLECT = 2
    SPHERE = 3
    FRANKEN = 4


class ButtonTypes(Enum):
    """The different types of floor buttons."""
    FLOOR = WEIGHTED = 0
    BOX = CUBE = 1
    BALL = SPHERE = 2


class FizzlerTypes(Enum):
    """The different types of fizzlers."""
    FIZZLER = 0
    LASERFIELD = 1


class GlassTypes(Enum):
    """The different types of glass."""
    GLASS = 0
    GRATE = GRATING = 1


# Actual properties begin here.
# First all the bools.

class StartEnabled(_BoolProp):
    """Generic Start Enabled option."""
    id = 'StartEnabled'
    instvar = '$start_enabled'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_start_enabled'


class StartReversed(_BoolProp):
    """Polarity value for Excursion Funnels."""
    id = 'StartReversed'
    instvar = '$start_reversed'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_start_reversed'


class StartDeployed(_BoolProp):
    """Starting position for Angled Panels."""
    id = 'StartDeployed'
    instvar = '$start_deployed'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_start_deployed'


class StartOpen(_BoolProp):
    """Specifies if the SP Exit Door starts open or not."""
    id = 'StartOpen'
    instvar = '$start_open'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_start_open'


class StartLocked(_BoolProp):
    """Specifies if the Coop Exit Door starts locked, or allows players to
    leave."""
    id = 'StartLocked'
    instvar = '$start_locked'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_coop_exit_starts_locked'


class FlipPanelPortalability(_BoolProp):
    """Specifies if the flip panel starts portalable."""
    id = 'portalable'
    instvar = '$start_deployed'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_portalable'


class CoopMode(_BoolProp):
    """For doors, specifies the map mode and therefore which door is used."""
    id = 'coopmode'
    instvar = ''  # Controls which item is used.
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_coop_puzzle'


class DropperEnabled(_BoolProp):
    """Enables or disables the dropper for Cubes and Paint."""
    id = 'DropperEnabled'
    instvar = ''  # Controls which item exports.
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_dropper_enabled'


class CubeAutoDrop(_BoolProp):
    """For cube droppers, decides if it triggers when the player enters.

    On ITEM_CUBE_DROPPER only, this exports inverted like the name suggests.
    """
    id = 'AutoDrop'
    instvar = '$disable_autodrop'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_auto_drop_cube'


class CubeAutoRespawn(_BoolProp):
    """For cube droppers, decides if it replaces destroyed cubes.

    On ITEM_CUBE_DROPPER only, this exports inverted like the name suggests.
    """
    id = 'AutoRespawn'
    instvar = '$disable_autorespawn'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_auto_respawn_cube'


class CubeFallStraightDown(_BoolProp):
    """A property which turns off some of the cube dropper's clips.

    This is always disabled.
    """
    id = 'itemfallstraightdown'
    instvar = '$item_fall_straight_down'
    trans_name = ''


# Track Platform prop types:


class TrackStartActive(_BoolProp):
    """Starting state for oscillating Track Platforms.

    If non-ocillating, this is disabled.
    """
    id = 'StartActive'
    instvar = '$start_active'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_rail_start_active'


class TrackIsOcillating(_BoolProp):
    """The mode for Track Platforms."""
    id = 'Oscillate'
    instvar = ''  # Picks instance
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_rail_oscillate'


class TrackStartingPos(_FloatProp):
    """The starting fractional position of Track Platforms."""
    id = 'StartingPosition'
    instvar = '$starting_position'


class TrackMoveDistance(_FloatProp):
    """The distance the Track Platform moves overall."""
    id = 'TravelDistance'
    instvar = '$travel_distance'


class TrackSpeed(_FloatProp):
    """The speed the Track Platform moves at.

    This is always 100 units/sec.
    """
    id = 'Speed'
    # Not really right, but should be about right.
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_paint_type_speed'
    instvar = '$speed'


class TrackMoveDirection(ItemProp[Angle]):
    id = 'TravelDirection'
    instvar = '$travel_direction'
    trans_name = ''  # Hidden prop

    @staticmethod
    def _parse_value(value: str) -> Angle:
        return Angle.from_str(value)


# Piston Platform:
# 4 T
# 3 |
# 2 |
# 1 |__
# 0


class PistonLowerExtent(ItemProp[int]):
    id = 'BottomLevel'
    instvar = '$bottom_level'
    trans_name = ''  # Controlled by the widgets.
    subtype_values = [0, 1, 2, 3]

    @staticmethod
    def _parse_value(value: str) -> int:
        try:
            pos = int(value)
            if 0 <= pos < 4:
                return pos
        except ValueError:
            raise ValueError(f'Invalid position {value}!') from None
        raise ValueError(f'Position {value} not in 0, 1, 2, 3!')


class PistonUpperExtent(ItemProp[int]):
    id = 'TopLevel'
    instvar = '$top_level'
    trans_name = ''  # Controlled by the widgets.
    subtype_values = [1, 2, 3, 4]

    @staticmethod
    def _parse_value(value: str) -> int:
        try:
            pos = int(value)
            if 0 < pos <= 4:
                return pos
        except ValueError:
            raise ValueError(f'Invalid position {value}!') from None
        raise ValueError(f'Position {value} not in 1, 2, 3, 4!')


class PistonStartUp(_BoolProp):
    """Determines if the piston begins at the upper or lower point."""
    id = 'StartUp'
    instvar = '$start_up'
    trans_name = ''  # Internal property.


class PistonAutoTrigger(_BoolProp):
    """Determines if the piston moves automatically."""
    id = 'AutoTrigger'
    instvar = '$allow_auto_trigger'
    trans_name = ''  # Internal property.


# Paint stuff.

class PaintTypeProp(ItemProp[PaintTypes]):
    """The main paint type property, directly specifying each paint type."""
    id = 'PaintType'
    instvar = ''  # Done through the other props.
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_paint_type'
    subtype_values = [
        PaintTypes.BOUNCE,
        PaintTypes.SPEED,
        PaintTypes.PORTAL,
        PaintTypes.ERASE,
        # This is not actually valid, but it works to get a single custom type.
        PaintTypes.REFLECT,
    ]
    _export_order = subtype_values

    @classmethod
    def _parse_value(cls, value: str) -> PaintTypes:
        """Parse the base paint type."""
        try:
            # Allow symbolic names.
            return PaintTypes[value.upper()]
        except KeyError:
            pass

        index = int(value)
        if 0 <= index < 5:
            return cls.subtype_values[index]
        raise ValueError(f'{value} is not a valid paint type!') from None

    @classmethod
    def _export_value(cls, value: PaintTypes) -> str:
        return str(cls._export_order.index(value))


class PaintExportType(PaintTypeProp):
    """An internal property that exports the actual paint type used.

    This matches the engine's paint type indexes.
    """
    id = 'PaintExportType'
    instvar = '$paint_type'
    trans_name = ''  # Internal prop.

    _paint_order = [
        PaintTypes.BOUNCE,
        PaintTypes.REFLECT,
        PaintTypes.SPEED,
        PaintTypes.PORTAL,
        PaintTypes.ERASE,
    ]


class PaintFlowType(ItemProp[PaintFlows]):
    """The amount of gel that drops."""

    id = 'PaintFlowType'
    # This actually sets multiple variables:
    # - $blobs_per_second
    # - $angled_blobs_per_second
    # - $streak_angle
    # - $ambient_sound
    # - $render_mode
    # The first is the most "important".
    instvar = '$blobs_per_second'
    trans_name = '$PORTAL2_PuzzleEditor_ContextMenu_paint_flow_type'
    subtype_values = list(PaintFlows)

    @staticmethod
    def _parse_value(value: str) -> PaintFlows:
        return PaintFlows(value)

    @staticmethod
    def _export_value(value: PaintFlows) -> str:
        return value.value


class PaintAllowStreaks(_BoolProp):
    """Specifies if the paint can streak across a surface.

    This actually exports either 0.35 or 0 to the instvar.
    """
    id = 'allowstreak'
    instvar = '$streak_time'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_allow_streak_paint'


class ConnectionCount(ItemProp[int]):
    """Tracks the number of input items."""
    id = 'ConnectionCount'
    instvar = "$connectioncount"
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_tbeam_activate'

    @staticmethod
    def _parse_value(value: str) -> int:
        count = int(value)
        if count < 0:
            raise ValueError('Connection count cannot be negative!')
        return count


class ConnectionCountPolarity(ConnectionCount):
    """Tracks the number of polairty-type input items for Funnels."""
    id = 'ConnectionCountPolarity'
    instvar = "$connectioncountpolarity"
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_tbeam_polarity'


class TimerDelay(ItemProp[int]):
    """The Timer Delay property, providing 0-30 second delays."""
    id = "TimerDelay"
    instvar = "$timer_delay"
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_timer_delay'

    @staticmethod
    def _parse_value(value: str) -> int:
        time = conv_int(value, 3)
        return max(0, min(30, time))

    def subtype_values(self) -> Sequence[int]:
        """Timers have a value from 0-30."""
        return range(0, 31)


class FaithVerticalAlignment(_BoolProp):
    """Specifies if a Faith Plate is in straight-up or angled mode."""
    id = 'VerticalAlignment'
    instvar = ''  # None!
    trans_name = ''  # Not visible.


class FaithSpeed(_FloatProp):
    """Stores the Faith Plate's speed, defining the arc height."""
    id = 'CatapultSpeed'
    instvar = '$catapult_speed'
    trans_name = ''  # Not visible.


class FaithTargetName(ItemProp[str]):
    """Logically would store or produce the name of the target.

    However, this never does anything.
    """
    id = 'Targetname'
    instvar = ''
    trans_name = ''

    @staticmethod
    def _parse_value(value: str) -> str:
        return value


class AngledPanelType(_EnumProp[PanelType]):
    """Differentiates between the two angled panel items."""
    id = 'AngledPanelType'
    instvar = ''  # None!
    trans_name = ''  # Not visible.
    subtype_values = list(PanelType)
    _enum = PanelType


class AngledPanelAnimation(ItemProp[PanelAnimation]):
    """The angle the panel rises to."""
    id = 'AngledPanelAnimation'
    instvar = 'animation'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_angled_panel_type'
    subtype_values = list(PanelAnimation)

    @classmethod
    def _parse_value(cls, value: str) -> PanelAnimation:
        value = value.casefold()
        if value.startswith('ramp_') and value.endswith('_deg_open'):
            value = value[5:-10]
        ind = int(value)
        if ind < 30:
            return cls.subtype_values[ind]
        else:
            return PanelAnimation(int(value))

    @staticmethod
    def _export_value(ang: PanelAnimation) -> str:
        return f'ramp_{ang.value}_deg_open'


class CubeTypeProp(_EnumProp[CubeTypes]):
    """Type of cubes."""
    id = 'CubeType'
    instvar = 'cubetype'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_cube_type'
    subtype_values = list(CubeTypes)
    _enum = CubeTypes


class ButtonTypeProp(_EnumProp[ButtonTypes]):
    """Type of floor buttons."""
    id = 'ButtonType'
    instvar = ''  # Sets instance index.
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_button_type'
    subtype_values = list(ButtonTypes)
    _enum = ButtonTypes


class FizzlerTypeProp(_EnumProp[FizzlerTypes]):
    """Type of fizzlers."""
    id = 'hazardtype'
    instvar = '$skin'
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_barrier_hazard_type'
    subtype_values = list(FizzlerTypes)
    _enum = FizzlerTypes


class GlassTypeProp(_EnumProp[GlassTypes]):
    """Type of fizzlers."""
    id = 'BarrierType'
    instvar = ''  # Brushes placed only
    trans_name = 'PORTAL2_PuzzleEditor_ContextMenu_barrier_type'
    subtype_values = list(GlassTypes)
    _enum = GlassTypes


# Finally add to the dict.
PROP_TYPES.update({
    # If no ID, it's an internal implementation
    # class.
    prop_type.id.casefold(): prop_type
    for prop_type in globals().values()
    if isinstance(prop_type, type)
       and hasattr(prop_type, 'id')
})

