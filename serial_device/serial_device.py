"""
SerialDevice class for connecting and communicating with a serial device
"""
import serial
import asyncio
import serial.tools.list_ports as list_ports
from curses.ascii import EOT
import readline  # NOQA


class SerialDevice:

    def __init__(self, id_prefix="", baudrate=115200, trans_end=chr(EOT)):
        """Initialization of the serial device interface"""
        self.id_prefix = id_prefix
        self.baudrate = baudrate
        self.trans_end = trans_end
        self.encoding = 'utf-8'
        self.timeout = 2
        self.open_delay = 2
        self.close_delay = 1
        self.devices = {}

    def _get_ports(self):
        """
        Returns a list of all available serial ports.
        The list is in reversed order because newly connected
        serial devices are usually located at the end of the list.
        """
        ports = sorted(
            [i.device for i in list(list_ports.comports())],
            reverse=True
        )
        return ports

    def _resolv_device(self, device):
        """Device resolver, returns the actual device object"""
        if device.__class__.__name__ == "Serial":
            return device
        elif device in self.devices:
            return self.devices[device]['device']
        else:
            return None

    async def _scan_port(self, port):
        """
        Tries to find a possibly connected serial device at the specified port.
        If a serial device is found it is added to the devices dictionary.

        Returns a boolean indicating if a serial device was found at the
        specified port.
        """
        success = False
        try:
            device = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                write_timeout=self.timeout,
                timeout=self.timeout
            )
        except serial.serialutil.SerialException:
            pass
        else:
            await asyncio.sleep(self.timeout)
            try:
                self.send(device, 'id')
            except serial.serialutil.SerialTimeoutException:
                device.close()
            else:
                reply = (
                    self.recv(device)
                ).strip(self.trans_end)
                if reply.startswith(self.id_prefix):
                    if reply not in self.devices:
                        self.devices[reply] = {
                            'port': port,
                            'device': device,
                        }
                    success = True
                device.close()
        return success

    async def _scan(self):
        """
        Scans for all connected serial devices and rebuilds self.devices
        Returns a list of device names found
        """
        self.devices = {}
        tasks = [self._scan_port(port) for port in self._get_ports()]
        await asyncio.gather(*tasks)
        return [key for key in self.devices.keys()]

    async def _open(self, device):
        """
        (Asynchronously) opens a device (if existing and not already opened).
        Returns a boolean indicating if the indicated device is open.
        """
        success = False
        open_device = self._resolv_device(device)
        if open_device is not None:
            open_device.open()
            await asyncio.sleep(self.open_delay)
            success = open_device.is_open
        return success

    async def _close(self, device):
        """
        (Asynchronoulsy) closes a device (if existing and opened).
        Returns a boolean indicating if the indicated device is NOT open.
        """
        success = True
        close_device = self._resolv_device(device)
        if close_device is not None:
            close_device.close()
            await asyncio.sleep(self.close_delay)
            success = not close_device.is_open
        return success

    def scan(self):
        """
        Synchronizes the asynchronous scan and returns the result
        """
        return asyncio.run(self._scan())

    def open(self, device):
        """
        (Synchronously) opens a device (if existing and not already opened).
        Returns a boolean indicating if the indicated device is open.
        """
        return asyncio.run(self._open(device))

    def close(self, device):
        """
        (Synchronoulsy) closes a device (if existing and opened).
        Returns a boolean indicating if the indicated device is NOT open.
        """
        return asyncio.run(self._close(device))

    def is_open(self, device):
        """Returns is_open attribute of a specific device"""
        return self._resolv_device(device).is_open

    def flush(self, device):
        """
        Flushes the serial input and output buffers of the indicated device
        (provided it exists and is open).
        """
        flush_device = self._resolv_device(device)
        if flush_device is not None:
            if flush_device.is_open:
                flush_device.reset_input_buffer()
                flush_device.reset_output_buffer()

    def send(self, device, data):
        """Implementation of the send functionality"""
        sender = self._resolv_device(device)
        if sender is not None:
            if sender.is_open:
                sender.write((data + self.trans_end).encode(self.encoding))

    def recv(self, device):
        """Implementation of the receive functionality"""
        reply = ''
        recvr = self._resolv_device(device)
        if recvr is not None:
            if recvr.is_open:
                try:
                    reply = recvr.read_until(
                        expected=self.trans_end.encode(self.encoding),
                    ).decode(self.encoding)
                except Exception as e:
                    print(e)
        return reply

    def cmd(self, device, cmd):
        """A send followed by a recv. Returns the result"""
        self.send(device, cmd)
        return self.recv(device)
