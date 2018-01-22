import subprocess as sub
import time
import asyncio
import locale
from contextlib import closing
import logging
import threading

class TcpDumpActivityMonitor():
    def __init__(self, sudo=False, port=None, net_interface=None):
        self.__sudo = sudo
        self.__port = port
        self.__net_interface=net_interface
        self.__last_active_time = None
        self.__tcpdump_proc = None
        self.__thread = None
        self.__kill_thread = False

    def __build_tcpdump_command(self):
        cmd = []
        if self.__sudo:
            cmd.append("sudo")
        cmd.append("tcpdump")
        cmd.append("-t")
        if self.__net_interface is not None:
            cmd.append("-i")
            cmd.append(self.__net_interface)
        if self.__port is not None:
            cmd.append("port")
            cmd.append(self.__port)
        return cmd

    async def start_monitoring_async(self):
        if self.__tcpdump_proc is not None:
            raise MonitoringInProgress("TcpDump monitoring is already in progress.")
        self.__last_active_time = time.time()
        cmd = self.__build_tcpdump_command()
        self.__tcpdump_proc = await asyncio.create_subprocess_exec(*cmd, stdout=sub.PIPE)

        try:
            async for line in self.__tcpdump_proc.stdout:
                logging.debug(line.decode(locale.getpreferredencoding(False)))
                self.__last_active_time = time.time()
        except asyncio.CancelledError:
            logging.info("cancelled tcpdump monitoring")
            pass

        if self.__tcpdump_proc.returncode is None:
            self.__tcpdump_proc.kill()
            await self.__tcpdump_proc.wait()
        self.__last_active_time = None

    def start_monitoring(self):
        if self.__tcpdump_proc is not None:
            raise MonitoringInProgress("TcpDump monitoring is already in progress.")
        self.__last_active_time = time.time()
        cmd = self.__build_tcpdump_command()
        self.__tcpdump_proc = sub.Popen(cmd, stdout=sub.PIPE)
        self.__thread = threading.Thread(target=self.__update_loop)
        self.__thread.daemon = True
        self.__thread.start()

    def __update_loop(self):
        for line in iter(self.__tcpdump_proc.stdout.readline, b''):
            logging.debug(line.decode(locale.getpreferredencoding(False)))
            self.__last_active_time = time.time()
            if self.__kill_thread:
                break


    def stop_monitoring(self):
        if self.__tcpdump_proc is None:
            return
        if self.__tcpdump_proc.returncode is None:
            self.__tcpdump_proc.kill()
            self.__tcpdump_proc.wait()
        self.__kill_thread = True
        self.__thread.join()
        self.__tcpdump_proc = None
        self.__last_active_time = None
        self.__thread = None
        self.__kill_thread = False

    def last_active_time(self):
        return self.__last_active_time


class MonitoringInProgress(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

if __name__ == '__main__':
    tcpdump = TcpDumpActivityMonitor(port="443")
    # loop = asyncio.get_event_loop()
    # with closing(loop):
    #     asyncio.ensure_future(tcpdump.start_monitoring_async(), loop=loop)
    #     asyncio.ensure_future(loop_call_async(tcpdump), loop=loop)
    #     loop.run_forever()

