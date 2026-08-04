#!/usr/bin/env python3
"""
v2ray订阅自动更新工具 (CI版)
在 GitHub Actions 中运行，无需本地环境。
从 wenpblog.com 抓取每日节点，生成 base64 订阅文件并提交到仓库。
"""

import re
import base64
import urllib.request
import ssl
import os
import sys
import json
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

LIST_URL = "https://www.wenpblog.com/list/5/1.html"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

NODE_PATTERNS = [
    r'vmess://[A-Za-z0-9+/=]+',
    r'vless://[^\s<>"\'#]+(?:#[^\s<>"\']*)?',
    r'trojan://[^\s<>"\'#]+(?:#[^\s<>"\']*)?',
    r'\bss://[A-Za-z0-9+/=@._:#-]+(?:#[^\s<>"\']*)?',
    r'\bssr://[A-Za-z0-9+/=]+',
]


def fetch_url(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def find_latest_post_url(list_html):
    pattern = r'href="(https://www\.wenpblog\.com/info/\d+\.html)"'
    matches = re.findall(pattern, list_html)
    if matches:
        return matches[0]
    pattern2 = r'href="(/info/\d+\.html)"'
    matches2 = re.findall(pattern2, list_html)
    if matches2:
        return "https://www.wenpblog.com" + matches2[0]
    return None


def extract_nodes(html):
    nodes = []
    seen = set()
    for pattern in NODE_PATTERNS:
        found = re.findall(pattern, html)
        for node in found:
            node = node.rstrip(',.;')
            node = node.replace('&amp;', '&')
            if '127.0.0.1' in node:
                continue
            if node not in seen:
                seen.add(node)
                nodes.append(node)
    return nodes


def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始更新v2ray订阅...")

    # Step 1: 获取列表页
    list_html = fetch_url(LIST_URL)
    print(f"列表页获取成功，长度: {len(list_html)} 字符")

    # Step 2: 找到最新文章URL
    latest_url = find_latest_post_url(list_html)
    if not latest_url:
        print("ERROR: 未能找到最新文章URL")
        return False
    print(f"最新文章URL: {latest_url}")

    # Step 3: 获取文章内容
    post_html = fetch_url(latest_url)
    print(f"文章内容获取成功，长度: {len(post_html)} 字符")

    # Step 4: 提取节点
    nodes = extract_nodes(post_html)

    if not nodes:
        print("ERROR: 未找到任何节点")
        return False

    print(f"共提取到 {len(nodes)} 个有效节点:")
    for i, node in enumerate(nodes, 1):
        display = node[:80] + ('...' if len(node) > 80 else '')
        print(f"  [{i}] {display}")

    # Step 5: 生成订阅文件
    raw_content = '\n'.join(nodes)
    encoded_content = base64.b64encode(raw_content.encode('utf-8')).decode('utf-8')

    sub_file = os.path.join(OUTPUT_DIR, 'v2ray_sub.txt')
    raw_file = os.path.join(OUTPUT_DIR, 'v2ray_nodes_raw.txt')

    with open(sub_file, 'w', encoding='utf-8') as f:
        f.write(encoded_content)
    print(f"Base64订阅文件已保存: {sub_file}")

    with open(raw_file, 'w', encoding='utf-8') as f:
        f.write(raw_content)
    print(f"原始节点列表已保存: {raw_file}")

    # 生成状态文件
    status = {
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'node_count': len(nodes),
        'source': latest_url,
    }
    status_file = os.path.join(OUTPUT_DIR, 'status.json')
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    print(f"状态文件已保存: {status_file}")

    print(f"订阅更新完成! 共 {len(nodes)} 个节点")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
