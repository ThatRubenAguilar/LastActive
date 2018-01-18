import configparser
import time


class Config:
    def __init__(self, file_path=None, config_refresh_time_sec=None):
        self.__parser = None
        self.__parser_file_path=file_path
        self.__config_refresh_time_threshold=config_refresh_time_sec
        self.__config_refresh_base_time=None
        self.__tcpdump_port="80"

        if file_path is not None:
            self.__config_refresh_base_time=time.perf_counter()
            self.__parser = configparser.ConfigParser()
            self.__populate_from_parser()

    def __populate_from_parser(self):
        parser = self.__parser
        file_path = self.__parser_file_path
        parser.read(file_path)
        self.__tcpdump_port=parser.get("TcpDump", "Port", fallback="80")

    def __check_for_config_refresh(self):
        if self.__config_refresh_time_threshold is not None and \
                self.__parser is not None and \
                self.__config_refresh_base_time - time.perf_counter() > self.__config_refresh_time_threshold:
            self.__config_refresh_base_time = time.perf_counter()
            self.__populate_from_parser()

    def tcpdump_port(self):
        self.__check_for_config_refresh()
        return self.__tcpdump_port