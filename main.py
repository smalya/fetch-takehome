import aiohttp
import argparse
import asyncio
import os
import yaml
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime


def load_config(file_path):
    """
    load endpoint configuration from the YAML file
    :param file_path:str Path to the YAML file
    :return:list A list of dicts
    """
    with open(file_path, 'r') as file:
        endpoints = yaml.safe_load(file)
        for endpoint in endpoints:
            endpoint['domain'] = urlparse((endpoint['url'])).hostname
    return endpoints

async def check_health(session, endpoint):
    """
    asynchronously performs health check of a single endpoint.
    :param session:aiohttp.ClientSession
    :param endpoint:dict A dictionary containing endpoint information
    :return: tuple (domain, status)
    """
    url = endpoint['url']
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers')
    json_body = endpoint.get('body')
    domain = endpoint['domain']
    status = 'DOWN'

    try:
        async with session.request(method=method, url=url, headers=headers, json=json_body,
                                   timeout=aiohttp.ClientTimeout(total=0.5)) as response:
            if 200 <= response.status < 300:
                status = 'UP'
    except Exception:
        pass
    return domain, status

async def monitor_endpoints(file_path, interval=15, log_file=None):
    """
    continuously monitor endpoints at a specified interval and logs availability
    :param file_path:str Path to the YAML file
    :param interval:int Number of seconds to wait between checks
    :param log_file:str Path to the log file
    :return:
    """
    config = load_config(file_path)
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"Run started at: {start_time}\n"
            tasks = [check_health(session, endpoint) for endpoint in config]
            results = await asyncio.gather(*tasks)
            domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
            for domain, result in results:
                domain_stats[domain]["total"] += 1
                if result == "UP":
                    domain_stats[domain]["up"] += 1

            # Log cumulative availability percentages
            for domain, stats in domain_stats.items():
                availability = round(100 * stats["up"] / stats["total"])
                log_message += f"{domain} has {availability}% availability percentage\n"
            log_message += "---\n"

            if log_file:
                with open(log_file, 'a') as log:
                    log.write(log_message)
            else:
                print(log_message)  # Default to printing if no log file is provided

            await asyncio.sleep(interval)

def parse_args():
    """
    parse command line arguments
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Monitor health of configured endpoints.")
    parser.add_argument("config", help="Path to the YAML config file")
    parser.add_argument("--interval", "-i", type=int, default=15,
                        help="Polling interval in seconds (default: 15)")
    # Default log file to be in the same directory as the script (main.py)
    default_logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitor_log.txt")
    parser.add_argument("--logfile", "-l", type=str, default=default_logfile,
                        help="Path to the log file where stats will be logged (default: current directory/monitor_log.txt)")

    return parser.parse_args()

# Entry point of the program
if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(monitor_endpoints(args.config, interval=args.interval, log_file=args.logfile))
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
