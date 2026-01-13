#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
验证 need_publish_to_skill 功能的测试脚本

这个脚本用于验证配置了 need_publish_to_skill: true 的智能体：
1. 会被正确导入和配置
2. 会被发布为技能（publish_to_bes: ["skill_agent"]）
3. 不会参与测试（不在 imported_agents 列表中）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json


def validate_cfg_json():
    """验证 cfg.json 中的配置"""
    print("="*80)
    print("验证 cfg.json 配置")
    print("="*80)

    cfg_file = "./data/data-agent/cfg.json"
    with open(cfg_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    agents = config.get("agents", [])
    excel_agent = None

    for agent in agents:
        if "excel数据映射及图表预设" in agent.get("agent_config", ""):
            excel_agent = agent
            break

    if not excel_agent:
        print("❌ 未找到 excel数据映射及图表预设.json 配置")
        return False

    print(f"\n✅ 找到配置: {excel_agent.get('agent_config')}")

    # 验证关键配置
    checks = [
        ("need_publish_to_skill", excel_agent.get("need_publish_to_skill"), True),
        ("need_run", excel_agent.get("need_run"), True),
        ("need_conf_llm", excel_agent.get("need_conf_llm"), True),
        ("skill_list", excel_agent.get("skill_list"), ["create_file"]),
    ]

    all_passed = True
    for key, actual, expected in checks:
        if actual == expected:
            print(f"  ✅ {key}: {actual}")
        else:
            print(f"  ❌ {key}: 期望 {expected}, 实际 {actual}")
            all_passed = False

    # test_queries 和 expected_results 应该为空（因为不参与测试）
    if excel_agent.get("test_queries") == {}:
        print(f"  ✅ test_queries: {{}} (空，因为不参与测试)")
    else:
        print(f"  ⚠️  test_queries: {excel_agent.get('test_queries')} (建议为空)")

    if excel_agent.get("expected_results") == {}:
        print(f"  ✅ expected_results: {{}} (空，因为不参与测试)")
    else:
        print(f"  ⚠️  expected_results: {excel_agent.get('expected_results')} (建议为空)")

    return all_passed


def validate_import_file():
    """验证导入文件是否存在"""
    print("\n" + "="*80)
    print("验证导入文件")
    print("="*80)

    import_file = "./data/data-agent/import/excel数据映射及图表预设.json"
    if os.path.exists(import_file):
        print(f"✅ 导入文件存在: {import_file}")
        return True
    else:
        print(f"❌ 导入文件不存在: {import_file}")
        return False


def validate_conftest_implementation():
    """验证 conftest.py 中的实现"""
    print("\n" + "="*80)
    print("验证 conftest.py 实现")
    print("="*80)

    conftest_file = "./testcases/data-agent/conftest.py"
    with open(conftest_file, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = [
        ("need_publish_to_skill 检查", 'need_publish_to_skill = agent_config_item.get("need_publish_to_skill"'),
        ("获取分类", "factory_client.GetCategory(AgentHeaders)"),
        ("发布配置 - skill_agent", '"publish_to_bes": ["skill_agent"]'),
        ("发布调用", "factory_client.PublishAgent(actual_agent_id, publish_config, AgentHeaders)"),
        ("排除测试", "agent_excluded_from_test"),
        ("else 分支 - 添加到测试", "imported_agents.append({"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name} - 未找到关键代码")
            all_passed = False

    return all_passed


def validate_factory_client():
    """验证 AgentFactory 类中的 PublishAgent 方法"""
    print("\n" + "="*80)
    print("验证 AgentFactory.PublishAgent 方法")
    print("="*80)

    factory_file = "./lib/data_agent/agent_factory.py"
    with open(factory_file, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = [
        ("PublishAgent 方法定义", "def PublishAgent(self, agent_id, publish_config, headers=None)"),
        ("API 路径", 'f"/agent-factory/v3/agent/{agent_id}/publish"'),
        ("POST 请求", "Request.post(self, url, publish_config, headers)"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name} - 未找到关键代码")
            all_passed = False

    return all_passed


def print_summary(results):
    """打印验证结果摘要"""
    print("\n" + "="*80)
    print("验证结果摘要")
    print("="*80)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {check_name}")

    print(f"\n总计: {passed}/{total} 项检查通过")

    if failed > 0:
        print(f"\n⚠️  有 {failed} 项检查失败，请检查相关配置和实现")
        return False
    else:
        print(f"\n✅ 所有检查通过！need_publish_to_skill 功能已正确实现")
        return True


def main():
    """主函数"""
    print("\n" + "="*80)
    print("need_publish_to_skill 功能验证")
    print("="*80)

    results = {
        "cfg.json 配置验证": validate_cfg_json(),
        "导入文件存在性验证": validate_import_file(),
        "conftest.py 实现验证": validate_conftest_implementation(),
        "AgentFactory API 方法验证": validate_factory_client(),
    }

    return print_summary(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
