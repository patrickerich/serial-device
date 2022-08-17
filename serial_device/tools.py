import asyncio
from serial_device.serial_device import SerialDevice


class SerialCmdLine(SerialDevice):

    def __init__(self, id_prefix="", baudrate=115200):
        super().__init__(id_prefix, baudrate)
        self.scan()

    def _print_selection(self):
        print("Please select a device from the list:")
        for key in self.devices.keys():
            print(key)

    def cmd_line(self, id=None):
        nr_devs = len(self.devices)
        if id is not None:
            if id in self.devices:
                print("Opening requested device!")
                self.run(id)
            else:
                print("Requested device not found!")
                self._print_select()
        elif nr_devs == 0:
            print("No device found!")
        elif nr_devs == 1:
            print("Found 1 suitable device candidate!")
            self.run(next(iter(self.devices)))
        else:
            print("Found multiple device candidates!")
            self._print_select()

    def run(self, id):
        print("Getting command line ready...")
        self.open(id)
        again = True
        while again:
            cmd = input(f"{id}:$ ")
            cmdsplit = cmd.split()
            if cmdsplit[0] == 'bye':
                again = False
            elif cmdsplit[0] == 'load':
                if len(cmd) >= 2:
                    self.load(id, cmdsplit[1])
                else:
                    print('Please specify filename')
            else:
                print(self.cmd(id, cmd))
        self.close(id)

    async def _load(self, id, filename):
        try:
            infile = open(filename, 'r')
        except IOError:
            print(f'Unable to open file {filename}')
        else:
            for line in infile:
                line = line.rstrip('\r\n')
                if line.startswith('#'):
                    print(line)
                else:
                    linesplit = line.split()
                    nr_items = len(linesplit)
                    if nr_items > 0:
                        if linesplit[0] == 'pause':
                            pkey = input(
                                'Press Enter to continue (a+Enter to abort): '
                            )
                            if pkey == 'a':
                                break
                        elif linesplit[0] == 'delay' and nr_items > 1:
                            try:
                                await asyncio.sleep(float(linesplit[1]))
                            except ValueError:
                                pass
                        else:
                            print(line)
                            self.flush(id)
                            print(self.cmd(id, line))

    def load(self, id, filename):
        return asyncio.run(self._load(id, filename))
