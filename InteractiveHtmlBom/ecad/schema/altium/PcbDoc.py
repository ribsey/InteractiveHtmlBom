from AltiumFile import AltiumBinaryFile
from olefile import OleFileIO


class PcbDoc(AltiumBinaryFile):
    def __init__(self, ole: OleFileIO):
        self._ole = ole

        self._elements = {}

        self._parseDefaultDirs(ole)
