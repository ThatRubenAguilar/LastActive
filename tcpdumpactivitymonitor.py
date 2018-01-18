import subprocess as sub
import time
import asyncio
import locale
from contextlib import closing
import logging

class TcpDumpActivityMonitor():
    def __init__(self, port="80"):
        self.__port = port
        self.__last_active_time = None

    async def start_monitoring_async(self):
        self.__last_active_time = time.time()
        cmd = ("sudo", "tcpdump", "port", self.__port, "-t")
        tcpdump_proc = await asyncio.create_subprocess_exec(*cmd, stdout=sub.PIPE)

        try:
            async for line in tcpdump_proc.stdout:
                logging.debug(line.decode(locale.getpreferredencoding(False)))
                self.__last_active_time = time.time()
        except asyncio.CancelledError:
            logging.info("cancelled tcpdump monitoring")
            pass

        if tcpdump_proc.returncode is None:
            #tcpdump_proc.kill()
            await tcpdump_proc.wait()
        self.__last_active_time = None

    def last_active_time(self):
        return self.__last_active_time


async def loop_call(dump):
    while True:
        print("what")
        print(dump.last_active_time())
        print(time.gmtime(dump.last_active_time()))
        await asyncio.sleep(3)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tcpdump = TcpDumpActivityMonitor(port="443")
    with closing(loop):
        asyncio.ensure_future(tcpdump.start_monitoring_async(), loop=loop)
        asyncio.ensure_future(loop_call(tcpdump), loop=loop)
        loop.run_forever()

