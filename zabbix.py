import requests

ZABBIX_URL = "http://loop21.miteleferico.bo:8080/api_jsonrpc.php"
API_TOKEN = "TU_TOKEN_AQUI"

HEADERS = {"Content-Type": "application/json-rpc"}

def zabbix_api(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "auth": API_TOKEN,
        "id": 1
    }
    r = requests.post(ZABBIX_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise Exception(data["error"])
    return data["result"]

def get_group_id(name):
    res = zabbix_api("hostgroup.get", {"filter": {"name": [name]}})
    return res[0]["groupid"] if res else None

def get_hosts(groupid):
    return zabbix_api("host.get", {
        "groupids": groupid,
        "output": ["hostid", "name"],
        "selectItems": ["key_", "lastvalue"]
    })
