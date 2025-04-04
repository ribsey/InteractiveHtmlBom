from olefile.olefile import OleFileIO, isOleFile
from AltiumError import AltiumError
import PcbDoc


class AltiumFileFactory():
    @staticmethod
    def getAltiumFile(path):
        if isOleFile(path):
            return AltiumFileFactory._getAltiumBinaryFile(path)
        else:
            raise AltiumError('Unknown file type')

    @staticmethod
    def _getAltiumBinaryFile(path):
        with OleFileIO(path) as ole:
            if ole.exists('FileHeaderSix'):
                header = str(ole.openstream('FileHeaderSix').read())
                if 'PCB 6.0 Binary File' in header:
                    return PcbDoc.PcbDoc(ole)
            else:
                raise AltiumError(
                    'Unknown file header - version maybe not supported')


if __name__ == '__main__':
    file = AltiumFileFactory.getAltiumFile(
        '/home/u568/Downloads/nucleo-32pins_sch/MB1180.PcbDoc')
