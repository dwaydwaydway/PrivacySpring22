from pathlib import Path

from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

EXP_NAME = 'with_category'


# The list of sites that we wish to crawl
sites = []
with open("urlsWcategory.csv", 'r') as file:
    for row in file:
        sites.append(row.strip().split(',')[0])
sites = sites[-2:]
# sites = [
#     # "https://www.mlb.com/",
    # "https://crinacle.com/",
#     # "https://www.amazon.com/",
#     "https://thechive.com/",
#     # "https://www.nydailynews.com/"
# ]

NUM_BROWSERS = min(len(sites), 8)

# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = True
    # Record Navigations
    browser_param.navigation_instrument = True
    # Record JS Web API calls
    browser_param.js_instrument = True
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = True
    # Record DNS resolution
    browser_param.dns_instrument = True

    tracking_protection=False

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path(f"./exp/{EXP_NAME}/")
manager_params.log_path = Path(f"./exp/{EXP_NAME}/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True


# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path(f"./exp/{EXP_NAME}/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
        )

        # Start by visiting the page
        # command_sequence.append_command(GetCommand(url=site, sleep=3), timeout=60)
        # Have a look at custom_command.py to see how to implement your own command
        command_sequence.get(sleep=1)
        command_sequence.recursive_dump_page_source()
        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)