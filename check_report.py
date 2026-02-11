# -*- coding: utf-8 -*-
"""
检查报告文件是否包含黄金分析
"""

import sys
import os
from pathlib import Path


def check_report_file(filepath):
    """检查报告文件内容"""
    print(f"检查文件: {filepath}")

    if not os.path.exists(filepath):
        print(f"  ❌ 文件不存在")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"  ✅ 文件存在，大小: {len(content)} 字符")

    # 检查关键内容
    checks = [
        ('黄金' in content, "包含'黄金'字样"),
        ('🥇' in content, "包含黄金emoji"),
        ('Au9999' in content, "包含Au9999代码"),
        ('GC=F' in content, "包含GC=F代码"),
        ('黄金投资分析' in content, "包含黄金章节"),
    ]

    for check, desc in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {desc}: {check}")

    # 显示黄金相关的内容片段
    if '黄金' in content:
        print("\n  黄金相关内容片段:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '黄金' in line or '🥇' in line or 'Au9999' in line or 'GC=F' in line:
                print(f"    行 {i+1}: {line[:100]}")

    return '黄金' in content or '🥇' in content


def main():
    """主函数"""
    print("=" * 60)
    print("检查报告文件中的黄金分析")
    print("=" * 60)

    # 检查可能的报告位置
    report_paths = [
        Path(__file__).parent / 'reports' / 'report_20260211.md',
        Path(__file__).parent / 'reports' / 'report_20250211.md',
        Path(__file__).parent / 'Result' / 'analysis-reports-27' / 'reports' / 'report_20260211.md',
        Path(__file__).parent / 'Result' / 'analysis-reports-27' / 'reports' / 'report_20250211.md',
    ]

    # 也检查 reports 目录下的所有 md 文件
    reports_dir = Path(__file__).parent / 'reports'
    if reports_dir.exists():
        for md_file in reports_dir.glob('*.md'):
            if md_file not in report_paths:
                report_paths.append(md_file)

    found_gold = False
    for path in report_paths:
        print(f"\n{'='*60}")
        if check_report_file(path):
            found_gold = True

    print("\n" + "=" * 60)
    if found_gold:
        print("✅ 找到包含黄金分析的报告")
    else:
        print("❌ 未找到包含黄金分析的报告")
        print("\n可能的原因:")
        print("1. 黄金分析未执行")
        print("2. 黄金分析执行失败")
        print("3. 报告生成时未包含黄金部分")
        print("4. 报告文件被覆盖或未保存")
    print("=" * 60)

    return 0 if found_gold else 1


if __name__ == "__main__":
    sys.exit(main())
