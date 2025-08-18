项目简介

这是一个用于检测 孚盟云 CRM 系统 /Ajax/LicMould.ashx 接口 SQL 注入漏洞 的批量 PoC 脚本
脚本支持单目标检测和多目标批量检测，并通过延时注入的方式判断漏洞是否存在

⚠️ 声明

本工具仅用于 安全研究与教学目的，请勿用于非法用途
对未授权的目标进行检测可能触犯法律，使用者需自行承担责任

使用方法
1. 环境要求

Python 3.x

第三方库：

pip install requests

2. 使用帮助

运行以下命令查看参数说明：

python poc.py -h


输出示例：

usage: Python poc.py [-u URL] [-f FILE]

孚盟云CRM /LicMould.ashx SQL注入漏洞

3. 单个目标检测
python poc.py -u http://example.com

4. 批量检测

把待检测的目标写入一个文本文件（每行一个 URL），例如 targets.txt：

http://site1.com

http://site2.com

http://site3.com


然后执行：

python poc.py -f targets.txt
