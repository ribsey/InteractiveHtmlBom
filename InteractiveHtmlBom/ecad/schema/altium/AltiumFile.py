from olefile.olefile import OleFileIO, OleStream
from AltiumError import AltiumError
from enum import Enum
import struct


class RecordId(Enum):
    arc6 = 1
    pad6 = 2
    via6 = 3
    track6 = 4
    text6 = 5
    fill6 = 6
    region6 = 11
    componentbody6 = 12


class PadShapeAlt(Enum):
    unknown = 0
    round = 1
    rect = 2
    octagonal = 3
    roundrectangle = 9


class PadModeRule(Enum):
    unknown = 0
    rule = 1
    manual = 2


class TextFontType(Enum):
    stroke = 0
    truetype = 1
    barcode = 2


class PadHoleType(Enum):
    normal = 0
    square = 1
    slot = 2


class Layer(Enum):
    f_cu = 1
    b_cu = 32


class Boolean(Enum):
    false = 0
    true = 1


class PadMode(Enum):
    simple = 0
    top_middle_bottom = 1
    full_stack = 2


class TextPosition(Enum):
    left_top = 1
    left_center = 2
    left_bottom = 3
    center_top = 4
    center_center = 5
    center_bottom = 6
    right_top = 7
    right_center = 8
    right_bottom = 9


class PadShape(Enum):
    unknown = 0
    circle = 1
    rect = 2
    octagonal = 3


class TextBarcodeType(Enum):
    code39 = 0
    code128 = 1


class AltiumFile():
    pass


class Xy():
    def __init__(self, bin: bytes):
        self.x = int.from_bytes(bin[0:3], 'little', signed=True)
        self.y = int.from_bytes(bin[4:7], 'little', signed=True)


class KeepoutRestrictions():
    def __init__(self, bin: bytes):
        # TODO
        # self.keepout_restriction_unknown = self._io.read_bits_int_be(3)
        # self.keepout_restriction_pth = self._io.read_bits_int_be(1) != 0
        # self.keepout_restriction_smd = self._io.read_bits_int_be(1) != 0
        # self.keepout_restriction_copper = self._io.read_bits_int_be(1) != 0
        # self.keepout_restriction_track = self._io.read_bits_int_be(1) != 0
        # self.keepout_restriction_via = self._io.read_bits_int_be(1) != 0
        pass


class Arc():
    def __init__(self, bin: bytes):
        if len(bin) < 56:
            raise IndexError
        self.layer = bin[0]
        self.flags = bin[1]  # bit1=is_not_polygonoutline, bit2=is_not_locked
        self.is_keepout = bin[2]
        self.net = int.from_bytes(bin[3:5], 'little')
        self.subpolyindex = int.from_bytes(bin[5:7], 'little')
        self.component = int.from_bytes(bin[7:9], 'little')
        # self._unnamed13 = bin[9:13]
        self.center = Xy(bin[13:20])
        self.radius = int.from_bytes(bin[21:25], 'little')
        self.start_angle = struct.unpack('<d', bin[25:33])[0]
        self.end_angle = struct.unpack('<d', bin[33:41])[0]
        self.width = int.from_bytes(bin[41:45], 'little')
        # self._unnamed19 = bin[45:56]
        if len(bin) >= 57:
            self.keepout_restrictions = KeepoutRestrictions(bin[56])


class AltiumBinaryFile(AltiumFile):
    def __init__(self):
        super().__init__()

        self._elements = {}

    def _parseArc(self, stream: OleStream):
        tmp = b' '
        while len(tmp) != 0:
            tmp = stream.read(1)

            if len(tmp) == 0:
                break

            recordId = RecordId(int.from_bytes(tmp, 'little'))

            if recordId != RecordId.arc6:
                raise AltiumError('Unexpected record ID')

            tmp = stream.read(4)

            if len(tmp) == 0:
                break

            length = int.from_bytes(tmp, 'little')

            tmp = stream.read(length)

            if len(tmp) == 0:
                break

            if len(tmp) != length:
                raise AltiumError('Could not read the expected length of data')

            if 'arc' not in self._elements:
                self._elements['arc'] = []

            self._elements['arc'].append(Arc(tmp))

        print(self._elements)

    _defaultStreamParsers = {
        'Arcs6/Data': _parseArc
    }

    def _parseDefaultDirs(self, file: OleFileIO):
        dirs = file.listdir()

        for dir in dirs:
            if len(dir) != 2:
                continue

            fullStreamName = '/'.join(dir)
            parser = self._defaultStreamParsers.get(fullStreamName, None)

            if parser is None:
                continue

            stream = file.openstream(fullStreamName)
            parser(self, stream)
