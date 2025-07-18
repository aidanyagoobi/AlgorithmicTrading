import re
def analyze_log(src):
    """
    Parses a trading system log file into a dictionary of timestamps and their associated fields.
"""
    #This dictionary will store the volume and price for each symbol
    log = {}
    with open(src, "r") as f:
       for line in f:
           timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', line)
           if not timestamp_match:
               continue
           timestamp = timestamp_match.group(1)
           information = dict(re.findall(r'(\w+)=(.+?)(?=\s\w+=|$|\s\|)',line))
           log[timestamp] = information #create a dictionary based on timestamps
    return log


def main():
    src = "trade_log.txt"
    cleaned_log = analyze_log(src)
    #Testing to see if the log functions correctly
    for key, value in cleaned_log.items():
        print("The timestamp is:", key, value)
    assert cleaned_log['2025-07-16T09:30:01Z']['LEVEL'] == 'ERROR'

if __name__ == "__main__":
    main()