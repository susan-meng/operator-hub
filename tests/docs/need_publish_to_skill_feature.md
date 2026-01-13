# need_publish_to_skill 功能说明

## 概述

`need_publish_to_skill` 是一个新的配置开关，用于控制智能体在导入并配置完成后，是否自动发布为技能。

## 功能特性

1. **自动发布为技能**：当 `need_publish_to_skill` 设置为 `true` 时，智能体会在配置完成后自动发布为技能
2. **不参与测试**：发布为技能的智能体不会添加到测试列表中，不会参与任何测试用例
3. **完整的发布流程**：自动获取分类、构造发布配置、调用发布API

## 配置示例

在 `data/data-agent/cfg.json` 中配置：

```json
{
    "agent_config": "excel数据映射及图表预设.json",
    "need_publish_to_skill": true,
    "need_run": true,
    "skill_list": ["create_file"],
    "test_queries": {},
    "expected_results": {}
}
```

## 实现细节

### 1. 配置参数说明

- `need_publish_to_skill`: `true/false` - 是否发布为技能
- `need_run`: 必须为 `true`，否则智能体不会被导入和配置
- `skill_list`: 需要配置的技能列表（如 `["create_file"]`）
- `test_queries`: 可以为空，因为不会参与测试
- `expected_results`: 可以为空，因为不会参与测试

### 2. 发布配置

发布为技能时，使用以下配置：

```python
publish_config = {
    "business_domain_id": "bd_public",
    "category_id": [category_id],  # 自动获取第一个可用分类
    "description": f"{agent_name} - 自动发布为技能",
    "publish_to_where": ["square"],
    "publish_to_bes": ["skill_agent"]  # 关键：发布为技能
}
```

### 3. 与发布为API的区别

| 发布类型 | `publish_to_bes` 值 | 用途 |
|---------|-------------------|------|
| 发布为技能 | `["skill_agent"]` | 智能体作为技能使用 |
| 发布为API | `["api_agent"]` | 智能体作为API使用 |

参考：`testcases/data-agent/api/test_agent_app.py:test_api_chat_completion`

### 4. 代码实现位置

主要实现在 `testcases/data-agent/conftest.py` 的 `AgentImport` fixture 中：

```python
# 检查是否需要发布为技能
need_publish_to_skill = agent_config_item.get("need_publish_to_skill", False)
if need_publish_to_skill:
    # 获取分类
    category_result = factory_client.GetCategory(AgentHeaders)
    # 构造发布配置
    publish_config = {
        "business_domain_id": "bd_public",
        "category_id": [category_id],
        "description": f"{agent_name} - 自动发布为技能",
        "publish_to_where": ["square"],
        "publish_to_bes": ["skill_agent"]
    }
    # 执行发布
    publish_result = factory_client.PublishAgent(actual_agent_id, publish_config, AgentHeaders)
    # 不添加到 imported_agents，不参与测试
else:
    # 添加到 imported_agents，参与测试
    imported_agents.append({...})
```

## 使用场景

这个功能适用于以下场景：

1. **技能预部署**：在测试环境中预先部署某些智能体作为技能，供其他智能体调用
2. **依赖管理**：某些智能体需要作为技能被其他智能体使用，但不需要独立测试
3. **环境准备**：自动准备测试环境所需的技能资源

## 注意事项

1. **分类要求**：系统中必须至少有一个可用的智能体分类，否则发布会失败
2. **权限要求**：需要有发布智能体的权限
3. **唯一性**：同一个智能体不能同时既参与测试又发布为技能
4. **清理策略**：发布为技能的智能体仍然会在测试结束时被删除（fixture的teardown阶段）

## 日志和监控

在 Allure 报告中会记录以下关键步骤：

- `publish_to_skill_start`: 开始发布为技能
- `publish_to_skill_success`: 发布成功
- `publish_to_skill_failure`: 发布失败
- `publish_to_skill_server_error`: 服务器错误
- `publish_to_skill_no_category`: 没有可用分类
- `publish_to_skill_category_error`: 获取分类失败
- `publish_to_skill_exception`: 发布异常
- `agent_excluded_from_test`: 智能体已发布为技能，不参与测试

## 测试验证

要验证这个功能是否正常工作：

1. 运行测试套件
2. 检查 Allure 报告中的 `publish_to_skill_*` 相关附件
3. 确认配置了 `need_publish_to_skill: true` 的智能体没有出现在测试用例中
4. 确认该智能体已被成功发布为技能（可以通过API验证）

## 示例

当前配置的示例：

**智能体**: `excel数据映射及图表预设.json`

**配置**:
- 需要发布为技能: `true`
- 配置LLM: `true`
- 配置技能: `["create_file"]`
- 不参与测试: 自动排除

**流程**:
1. 导入智能体
2. 配置LLM模型
3. 配置技能（create_file）
4. 发布为技能（publish_to_bes: ["skill_agent"]）
5. 不添加到测试列表
6. 测试结束后删除
