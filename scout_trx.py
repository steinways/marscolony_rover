"""
Script to get mappings of plot id -> address and address -> [plot] on marscolony on Harmony
"""

import requests
import json
from collections import defaultdict
import pandas as pd

ADDRESS = '0x0d112a449d23961d03e906572d8ce861c441d6c3' # marscolony address
BASE_URL = 'https://api.s0.t.hmny.io/'
JSON_PAYLOAD = {
                "jsonrpc":"2.0",
                "method":"hmyv2_getTransactionsHistory",
                "id":1,
                "params":[]
                }

def get_transactions(payload_template, address, page_idx, limit):
    payload_template["params"] = [{"fullTx":True,"txType":"ALL","order":"DESC","address":address,"pageIndex":page_idx,"pageSize":limit}]
    try:
        response = requests.post(BASE_URL, json=payload_template)
    except:
        return []
    data = json.loads(response.text)
    return data['result']['transactions']

if __name__ == "__main__":
    page_index, limit_max = 0, 100
    map_address_plots = defaultdict(list)
    map_plot_address = {}
    response = get_transactions(JSON_PAYLOAD, ADDRESS, page_index, limit_max)

    while (len(response) != 0):
        print(f"Retrieving from Page Index: {page_index}")
        for r in response:
            input_hex = r['input']
            func_name = input_hex[:10]
            if func_name != "0x66233126": # claimOne() Method
                continue
            sender = r['from']
            plot_id = int(input_hex[-4:], 16) # last four hex character in input corresponds to land plot ID
            map_address_plots[sender].append(plot_id)
            map_plot_address[plot_id] = sender
        page_index += 1
        response = get_transactions(JSON_PAYLOAD, ADDRESS, page_index, limit_max)
            
    df = pd.DataFrame(zip(map_plot_address.keys(), map_plot_address.values()), columns=['plot_id', 'address'])
    df.to_csv("marscolony.csv", index=False)
    