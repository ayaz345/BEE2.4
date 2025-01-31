from __future__ import annotations
from typing import Sequence
import base64

import attrs
from srctools import Property, bool_as_int, logger
from srctools.dmx import Element

import config


LOGGER = logger.get_logger(__name__, 'conf.comp_pane')
PLAYER_MODEL_ORDER: Sequence[str] = ['PETI', 'SP', 'ATLAS', 'PBODY']


@config.APP.register
@attrs.frozen(slots=False)
class CompilePaneState(config.Data, conf_name='CompilerPane'):
    """State saved in palettes.

    Note: We specifically do not save/load the following:
        - packfile dumping
        - compile counts
    This is because these are more system-dependent than map dependent.
    """
    sshot_type: str = 'PETI'
    sshot_cleanup: bool = False
    sshot_cust: bytes = attrs.field(repr=False, default=b'')
    spawn_elev: bool = False
    player_mdl: str = 'PETI'
    use_voice_priority: bool = False

    @classmethod
    def parse_legacy(cls, conf: Property) -> dict[str, CompilePaneState]:
        """Parse legacy config data."""
        # No change from new KV1 format.
        return {'': cls.parse_kv1(
            conf.find_key('CompilerPane', or_blank=True),
            1,
        )}

    @classmethod
    def parse_kv1(cls, data: Property, version: int) -> CompilePaneState:
        """Parse Keyvalues1 format data."""
        if 'sshot_data' in data:
            screenshot_parts = b'\n'.join([
                prop.value.encode('ascii')
                for prop in
                data.find_children('sshot_data')
            ])
            screenshot_data = base64.decodebytes(screenshot_parts)
        else:
            screenshot_data = b''

        sshot_type = data['sshot_type', 'PETI'].upper()
        if sshot_type not in ['AUTO', 'CUST', 'PETI']:
            LOGGER.warning('Unknown screenshot type "{}"!', sshot_type)
            sshot_type = 'AUTO'

        player_mdl = data['player_model', 'PETI'].upper()
        if player_mdl not in PLAYER_MODEL_ORDER:
            LOGGER.warning('Unknown player model "{}"!', player_mdl)
            player_mdl = 'PETI'

        return CompilePaneState(
            sshot_type=sshot_type,
            sshot_cleanup=data.bool('sshot_cleanup', False),
            sshot_cust=screenshot_data,
            spawn_elev=data.bool('spawn_elev', False),
            player_mdl=player_mdl,
            use_voice_priority=data.bool('voiceline_priority', False),
        )

    def export_kv1(self) -> Property:
        """Generate keyvalues1 format data."""
        props = Property('', [
            Property('sshot_type', self.sshot_type),
            Property('sshot_cleanup', bool_as_int(self.sshot_cleanup)),
            Property('spawn_elev', bool_as_int(self.spawn_elev)),
            Property('player_model', self.player_mdl),
            Property('voiceline_priority', bool_as_int(self.use_voice_priority)),
        ])

        # Embed the screenshot in so we can load it later.
        if self.sshot_type == 'CUST':
            # encodebytes() splits it into multiple lines, which we write
            # in individual blocks to prevent having a massively long line
            # in the file.
            props.append(Property(
                'sshot_data',
                [
                    Property('b64', data) for data in
                    base64.encodebytes(self.sshot_cust).decode('ascii').splitlines()
                ]
            ))
        return props

    def export_dmx(self) -> Element:
        """Generate DMX format data."""
        elem = Element('CompilerPaneState', 'DMElement')
        elem['sshot_type'] = self.sshot_type
        elem['sshot_cleanup'] = self.sshot_cleanup
        elem['spawn_elev'] = self.spawn_elev
        elem['player_model'] = self.player_mdl
        elem['voiceline_priority'] = self.use_voice_priority
        if self.sshot_type == 'CUST':
            elem['sshot_data'] = self.sshot_cust
        return elem
