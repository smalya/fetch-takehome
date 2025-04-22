# Endpoint Health Monitoring Script

This script monitors the health of configured endpoints, calculates their availability and logs the results.

## Requirements
- Python 3.6 or higher
- Dependencies listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/smalya/fetch-takehome.git
   cd fetch-takehome
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the script:
   ```bash
   python3 main.py sample.yaml --interval 15
   ```
   run the script with custom log file path
    ```bash
   python3 main.py sample.yaml --interval 15 --logfile monitor_log.txt
   ```

## Config File Format

The `sample.yaml` file should be in the following format:

```yaml
- url: "http://example.com/health"
  method: "GET"
  headers:
    Content-Type: "application/json"
```

## Code changes

- Port numbers were not being ignored while parsing domain. Used urllib library to extract only hostname.
- Added argument parser to read command line arguments and make it user-friendly. Also, set defaults when arguments are 
not specified.
- Added the ability to specify the interval as a command-line argument. This makes the program more configurable and 
allows users to adjust the frequency of check cycles.
- Added enhancement to log availability and store in a text file instead of just printing. Added timestamp to the log 
results. This approach ensures that all monitoring results are logged and saved, allowing you to track availability over
time, even if the script is stopped and restarted.
- check_health was not looking for condition if endpoint response is less than 500ms. Added a timeout in the request to 
mark status as DOWN if response time is greater than 500ms.
- The domain stats are not getting reset to 0 before each check cycle. Changed the code to initialize domain stats 
before each cycle.
- Transitioned from using the synchronous requests library to asynchronous aiohttp and asyncio libraries. Instead of
waiting for each HTTP request to complete before starting the next, defined asynchronous functions using async def
and used await to handle requests without blocking. By leveraging asyncio.gather, multiple URLs can be fetched 
concurrently, significantly improving the speed and responsiveness of the script.
