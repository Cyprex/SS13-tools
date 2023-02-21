"""Abstract implementation of a log downloader"""
from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import Generator, Iterable, Annotated, Union
from itertools import product

from aiohttp import ClientSession
from colorama import Fore
from dateutil.parser import isoparse
from tqdm.asyncio import tqdm

from .constants import DEFAULT_OUTPUT_PATH, GAME_TXT_URL, GAME_TXT_ADMIN_URL, DEFAULT_FILES
from ..constants import USER_AGENT
from ..scrubby import RoundData


class LogDownloader(ABC):
    """Log downloader object. For downloading logs.
    Either pass the arguments in the constructor or call `interactive()`"""

    tgforums_cookie: Annotated[str, "Forum cookie if you want raw logs"] = ""
    user_agent: Annotated[str, "User agent so people know who keeps spamming requests (and for raw logs)"] = USER_AGENT
    output_path: Annotated[str, "Where should we write the file to?"] = DEFAULT_OUTPUT_PATH
    rounds: Annotated[list[RoundData], "The list of rounds to download"] = []
    files: Annotated[list[str], "Which files do we want to dowload?"] = DEFAULT_FILES

    def authenticate(self) -> bool:
        """Tries to authenticate against the TG forums"""

    def authenticate_interactive(self) -> bool:
        """Tries to authenticate against the TG forums interactively"""
        if input("Would you like to log in? ").lower() not in ['y', 'yes', 'true', '1']:
            return False
        return self.authenticate()

    @abstractmethod
    async def update_round_list(self) -> None:  # Not the best way of doing it but I can't be bothered right now
        """Generates a list of rounds and saves it to self.rounds"""

    def get_log_links(self) -> Iterable[str]:
        """Gets the links of logs we want to download"""
        url = GAME_TXT_ADMIN_URL if self.tgforums_cookie else GAME_TXT_URL
        for round_data, file_name in product(self.rounds, self.files):
            round_data.timestamp = isoparse(round_data.timestamp)
            yield round_data, url.format(
                server=round_data.server.lower().replace('bagil', 'basil'),
                year=str(round_data.timestamp.year),
                month=f"{round_data.timestamp.month:02d}",
                day=f"{round_data.timestamp.day:02d}",
                round_id=round_data.roundID,
                file_name=file_name
            )

    @abstractmethod
    def filter_lines(self, logs: list[bytes]) -> Iterable[bytes]:
        """Filters lines from a log file, returning only the ones we want"""

    async def get_logs_async(self) -> Generator[tuple[RoundData, Union[list[bytes], None]], None, None]:
        """This is a generator that yields a tuple of the `RoundData` and list of round logs, for all rounds in `rounds`

        if `output_bytes` is true, the function will instead yield `bytes` instead of `str`

        On 404, the list will be None instead"""
        async with ClientSession(cookies={"tgforums_sid": self.tgforums_cookie},
                                 headers={"User-Agent": self.user_agent}) as session:
            tasks = []

            async def fetch(round_data: RoundData, link: str):
                # Edge case warning: if we go beyond the year 2017 or so, the logs path changes.
                # I don't expect anyone to go that far so I won't be doing anything about it
                async with session.get(link) as rsp:
                    if not rsp.ok:
                        return round_data, None
                    return round_data, await rsp.read()

            for round_data, link in self.get_log_links():
                tasks.append(asyncio.ensure_future(fetch(round_data, link)))

            # This could be out of order but we don't really care, it's not important
            for task in tasks:
                response: bytes
                round_data, response = await task
                if not response:
                    yield round_data, None
                else:
                    yield round_data, response.split(b"\r\n")

            await asyncio.gather(*tasks)

    @staticmethod
    def format_line_bytes(line: bytes, round_data: RoundData) -> list[str]:
        """Takes the raw line and formats it to `{server_name} {round_id} | {unmodified line}`"""
        return round_data.server.encode("utf-8") + b" " + str(round_data.roundID).encode("utf-8") + b" | " + line + b"\n"

    async def process_and_write(self, output_path: str = None):
        """Processes the data, downloads the logs and saves them to a file"""
        output_path = output_path or self.output_path
        if not self.rounds:
            await self.update_round_list()
        with open(output_path, 'wb') as file:
            pbar = tqdm(self.get_logs_async(), total=len(self.rounds)*len(self.files))
            async for round_data, logs in pbar:
                # Type hints
                round_data: RoundData
                logs: list[bytes]

                pbar.set_description(f"Getting ID {round_data.roundID} on {round_data.server}")
                if not logs:
                    pbar.clear()
                    print(f"{Fore.YELLOW}WARNING:{Fore.RESET} Could not find round " +
                          f"{round_data.roundID} on {round_data.server}")
                    pbar.display()
                    continue
                if round_data.roundStartSuicide:
                    pbar.clear()
                    print(f"{Fore.MAGENTA}WARNING:{Fore.RESET} round start suicide " +
                          f"in round {round_data.roundID} on {round_data.server}")
                    pbar.display()
                for line in self.filter_lines(logs):
                    file.write(self.format_line_bytes(line, round_data))

    @staticmethod
    @abstractmethod
    def interactive() -> LogDownloader:
        """Interactively set variables"""