import sys
from getpass import getpass
import hashlib
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
#pylint: enable=E0401
#pylint: enable=C0413

class Token(Ice.Application):
    def run(self, argv):
        proxy=self.communicator().stringToProxy(argv[2])
        authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authentication:
            raise RuntimeError('Invalid proxy')
        try:
            print("Introduce la contraseña: ")
            current_pass = getpass()
            token = authentication.getNewToken(argv[1], current_pass)
            print("New token: "+token)
        except IceGauntlet.Unauthorized:
            print("Unauthorized")

sys.exit(Token().main(sys.argv))
