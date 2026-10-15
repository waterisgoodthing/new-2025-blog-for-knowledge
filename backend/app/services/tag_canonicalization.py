from __future__ import annotations

import re
from collections import defaultdict

CANONICAL_CLUSTERS: dict[str, list[str]] = {
    "以太网交换": ["交换机", "直通交换", "存储转发", "以太网", "交换", "交换技术"],
    "子网划分": ["子网", "子网掩码", "subnet", "VLSM"],
    "IP路由": ["路由", "路由器", "路由表", "静态路由", "动态路由", "RIP", "OSPF"],
    "TCP协议": ["TCP", "传输控制协议", "三次握手", "四次挥手", "可靠传输", "流量控制", "拥塞控制"],
    "UDP协议": ["UDP", "用户数据报协议"],
    "ARP协议": ["ARP", "地址解析", "RARP"],
    "DNS协议": ["DNS", "域名解析", "域名系统"],
    "HTTP协议": ["HTTP", "HTTPS", "Web", "网页"],
    "网络层": ["网络层", "IP协议", "IPv4", "IPv6", "ICMP"],
    "数据链路层": ["数据链路层", "MAC", "帧", "差错控制"],
    "物理层": ["物理层", "信号", "编码", "调制"],
    "传输层": ["传输层", "端口", "套接字", "socket"],
    "应用层": ["应用层"],
    "网络安全": ["防火墙", "VPN", "加密", "认证", "SSL", "TLS"],
    "无线网络": ["WiFi", "WLAN", "无线", "802.11"],
    "广播地址": ["广播", "广播地址", "broadcast"],
    "网络地址": ["网络号", "网络地址", "network address"],
    "CIDR表示法": ["CIDR", "斜线记法", "无类域间路由"],
    "滑动窗口": ["滑动窗口", "窗口", "GBN", "SR"],
    "拥塞控制": ["拥塞", "慢开始", "快重传", "快恢复", "AIMD"],
}

_LOW_VALUE_TAGS = {
    "解析清晰", "解析详细", "答案正确", "重要", "常见", "基础", "典型",
    "必考", "高频", "核心", "关键", "易错", "难点", "重点",
    "复习", "练习", "巩固", "总结", "归纳",
}

_reverse_map: dict[str, str] | None = None


def _get_reverse_map() -> dict[str, str]:
    global _reverse_map
    if _reverse_map is None:
        _reverse_map = {}
        for canonical, aliases in CANONICAL_CLUSTERS.items():
            _reverse_map[canonical.lower()] = canonical
            for alias in aliases:
                _reverse_map[alias.lower()] = canonical
    return _reverse_map


def canonicalize_tag(raw: str) -> str | None:
    cleaned = raw.strip()
    if not cleaned:
        return None
    if cleaned in _LOW_VALUE_TAGS:
        return None
    if len(cleaned) == 1 and not ('\u4e00' <= cleaned <= '\u9fff'):
        return None
    rmap = _get_reverse_map()
    return rmap.get(cleaned.lower(), cleaned)


def canonicalize_tags(raw_tags: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in raw_tags:
        canonical = canonicalize_tag(raw)
        if canonical and canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result


def get_canonical_cluster(raw_kp: str) -> tuple[str, list[str]]:
    rmap = _get_reverse_map()
    canonical = rmap.get(raw_kp.strip().lower(), raw_kp.strip())
    aliases = []
    for c, als in CANONICAL_CLUSTERS.items():
        if c == canonical:
            aliases = als
            break
    return canonical, aliases


def group_knowledge_points(raw_kps: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for kp in raw_kps:
        canonical, _ = get_canonical_cluster(kp)
        groups[canonical].append(kp)
    return dict(groups)
