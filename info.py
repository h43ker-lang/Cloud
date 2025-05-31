import requests

def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']

def get_ip_info(ip):
    response = requests.get(f'http://ip-api.com/json/{ip}')
    return response.json()

def print_ip_info(info):
    print("\n[+] IP Information")
    print(f"IP Address: {info.get('query')}")
    print(f"Country:    {info.get('country')}")
    print(f"Region:     {info.get('regionName')}")
    print(f"City:       {info.get('city')}")
    print(f"ZIP:        {info.get('zip')}")
    print(f"ISP:        {info.get('isp')}")
    print(f"Org:        {info.get('org')}")
    print(f"AS:         {info.get('as')}")
    print(f"Timezone:   {info.get('timezone')}")
    print(f"Lat/Lon:    {info.get('lat')}, {info.get('lon')}")
    print()

def main():
    try:
        print("[*] Getting public IP...")
        ip = get_public_ip()
        print(f"[+] Public IP: {ip}")

        print("[*] Getting IP info...")
        info = get_ip_info(ip)
        print_ip_info(info)

    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    main()
