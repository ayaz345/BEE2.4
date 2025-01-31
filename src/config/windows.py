from __future__ import annotations

from typing import Dict, Mapping
import attrs
from srctools import Property, conv_bool, bool_as_int, logger
from srctools.dmx import Attribute, Element, ValueType, Vec2

from BEE2_config import GEN_OPTS as LEGACY_CONF
import config

LOGGER = logger.get_logger(__name__, 'conf.win')


@config.APP.register
@attrs.frozen(slots=False)
class WindowState(config.Data, conf_name='PaneState', uses_id=True, palette_stores=False):
    """Holds the position and size of windows."""
    x: int
    y: int
    width: int = -1
    height: int = -1
    visible: bool = True

    @classmethod
    def parse_legacy(cls, conf: Property) -> Dict[str, 'WindowState']:
        """Convert old GEN_OPTS configuration."""
        opt_block = LEGACY_CONF['win_state']
        names: set[str] = set()
        for name in opt_block.keys():
            try:
                name, _ = name.rsplit('_', 1)
            except ValueError:
                continue
            names.add(name)
        return {
            name: WindowState(
                x=LEGACY_CONF.getint('win_state', f'{name}_x', -1),
                y=LEGACY_CONF.getint('win_state', f'{name}_y', -1),
                width=LEGACY_CONF.getint('win_state', f'{name}_width', -1),
                height=LEGACY_CONF.getint('win_state', f'{name}_height', -1),
                visible=LEGACY_CONF.getboolean(
                    'win_state', f'{name}_visible', True
                ),
            )
            for name in names
        }

    @classmethod
    def parse_kv1(cls, data: Property, version: int) -> 'WindowState':
        """Parse keyvalues1 data."""
        assert version == 1, version
        return WindowState(
            data.int('x', -1),
            data.int('y', -1),
            data.int('width', -1),
            data.int('height', -1),
            data.bool('visible', True),
        )

    def export_kv1(self) -> Property:
        """Create keyvalues1 data."""
        prop = Property('', [
            Property('visible', '1' if self.visible else '0'),
            Property('x', str(self.x)),
            Property('y', str(self.y)),
        ])
        if self.width >= 0:
            prop['width'] = str(self.width)
        if self.height >= 0:
            prop['height'] = str(self.height)
        return prop

    @classmethod
    def parse_dmx(cls, data: Element, version: int) -> 'WindowState':
        """Parse DMX configuation."""
        assert version == 1, version
        pos = data['pos'].val_vec2 if 'pos' in data else Vec2(-1, -1)
        return WindowState(
            x=int(pos.x),
            y=int(pos.y),
            width=data['width'].val_int if 'width' in data else -1,
            height=data['height'].val_int if 'height' in data else -1,
            visible=data['visible'].val_bool if 'visible' in data else True,
        )

    def export_dmx(self) -> Element:
        """Create DMX configuation."""
        elem = Element('', '')
        elem['visible'] = self.visible
        elem['pos'] = Attribute.vec2('pos', (self.x, self.y))
        if self.width >= 0:
            elem['width'] = self.width
        if self.height >= 0:
            elem['height'] = self.height
        return elem


@config.APP.register
@attrs.frozen(slots=False)
class SelectorState(config.Data, conf_name='SelectorWindow', palette_stores=False, uses_id=True):
    """The state for selector windows for restoration next launch."""
    open_groups: Mapping[str, bool] = attrs.Factory(dict)
    width: int = 0
    height: int = 0

    @classmethod
    def parse_legacy(cls, conf: Property) -> dict[str, SelectorState]:
        """Convert the old legacy configuration."""
        result: dict[str, SelectorState] = {
            prop.name: cls.parse_kv1(prop, 1)
            for prop in conf.find_children('Selectorwindow')
        }
        return result

    @classmethod
    def parse_kv1(cls, data: Property, version: int) -> SelectorState:
        """Parse from keyvalues."""
        assert version == 1
        open_groups = {
            prop.name: conv_bool(prop.value)
            for prop in data.find_children('Groups')
        }
        return cls(
            open_groups,
            data.int('width', -1), data.int('height', -1),
        )

    def export_kv1(self) -> Property:
        """Generate keyvalues."""
        props = Property('', [])
        with props.build() as builder:
            builder.width(str(self.width))
            builder.height(str(self.height))
            with builder.Groups:
                for name, is_open in self.open_groups.items():
                    builder[name](bool_as_int(is_open))
        return props

    @classmethod
    def parse_dmx(cls, data: Element, version: int) -> SelectorState:
        """Parse DMX elements."""
        assert version == 1
        open_groups: Dict[str, bool] = {
            name.casefold(): False for name in data['closed'].iter_str()
        }
        for name in data['opened'].iter_str():
            open_groups[name.casefold()] = True

        return cls(open_groups, data['width'].val_int, data['height'].val_int)

    def export_dmx(self) -> Element:
        """Serialise the state as a DMX element."""
        elem = Element('WindowState', 'DMElement')
        elem['width'] = self.width
        elem['height'] = self.height
        elem['opened'] = opened = Attribute.array('opened', ValueType.STRING)
        elem['closed'] = closed = Attribute.array('closed', ValueType.STRING)
        for name, val in self.open_groups.items():
            (opened if val else closed).append(name)
        return elem
