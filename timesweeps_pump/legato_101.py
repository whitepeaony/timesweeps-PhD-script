from syringe_pump import Pump
import aioserial


class Legato101(Pump):
    """Patch for the Legato 101 pump, which does not conform to docs and needs `nvram off`"""

    async def _initialise(self):
        """Ensure the pump is configured correctly to receive commands."""
        self._initialised = True
        await self._write("poll on")
        # disable NVRAM storage which could be damaged by repeated writes
        await self._write("nvram off")

    @classmethod
    async def from_serial(cls, serial: aioserial.AioSerial):
        self = cls(serial=serial)
        await self._initialise()
        return self
