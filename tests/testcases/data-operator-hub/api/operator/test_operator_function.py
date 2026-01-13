# -*- coding:UTF-8 -*-

import allure
import pytest
import random
import string
import time

from lib.operator import Operator

@allure.feature("算子注册与管理接口测试：函数算子测试")
class TestOperatorFunction:
    """
    本测试类验证 'metadata_type: function' 类型的算子注册与管理。
    
    设计背景：
    算子支持两种元数据类型：OpenAPI 和 Function。
    Function 类型的算子直接包含 Python 代码片段，不需要外部 OpenAPI 文件。
    
    测试重点：
    1. Function 算子的注册逻辑（function_input 字段）。
    2. Function 算子的编辑逻辑。
    3. Function 算子的执行模式限制（目前通常为同步）。
    """
    
    client = Operator()

    @allure.title("注册函数算子，传参正确，注册成功")
    def test_register_function_operator_01(self, Headers):
        name = 'func_op_' + ''.join(random.choice(string.ascii_letters) for i in range(5))
        
        function_input = {
            "name": name,
            "description": "test function operator",
            "code": "def handler(event, context):\n    return {'statusCode': 200, 'body': 'hello'}",
            "script_type": "python",
            "inputs": [
                {"name": "param1", "type": "string", "required": True}
            ],
            "outputs": [
                {"name": "result", "type": "string"}
            ]
        }
        
        data = {
            "operator_metadata_type": "function",
            "function_input": function_input,
            "operator_info": {
                "category": "data_process",
                "execution_mode": "sync"
            }
        }
        
        result = None
        for i in range(3):
            result = self.client.RegisterOperator(data, Headers)
            if result[0] == 200: break
            time.sleep(1)
            
        assert result[0] == 200, f"注册函数算子失败: {result}"
        assert result[1][0]["status"] == "success"
        operator_id = result[1][0]["operator_id"]
        
        # 验证获取信息
        res = self.client.GetOperatorInfo(operator_id, Headers)
        assert res[0] == 200
        assert res[1]["metadata_type"] == "function"
        assert res[1]["metadata"]["function_content"]["code"] == function_input["code"]

    @allure.title("编辑函数算子代码，编辑成功，生成新版本")
    def test_edit_function_operator_01(self, Headers):
        # 1. 注册
        name = 'func_edit_' + ''.join(random.choice(string.ascii_letters) for i in range(5))
        function_input = {
            "name": name,
            "code": "def handler(event):\n    return 'v1'",
            "script_type": "python",
            "inputs": [],
            "outputs": []
        }
        data = {
            "operator_metadata_type": "function",
            "function_input": function_input,
            "description": "initial function desc"
        }
        reg_res = self.client.RegisterOperator(data, Headers)
        assert reg_res[0] == 200
        operator_id = reg_res[1][0]["operator_id"]
        v1 = reg_res[1][0]["version"]
        
        # 2. 编辑代码
        # 补全 function_input 内部的所有字段，特别是 name 必须与注册时保持一致
        edit_data = {
            "operator_id": operator_id,
            "metadata_type": "function",
            "description": "updated function desc",
            "function_input": {
                "name": name,  # 必须与注册时的名称一致
                "description": "updated function desc",
                "code": "def handler(event, context):\n    return {'body': 'v2'}",
                "script_type": "python",
                "inputs": [
                    {"name": "param1", "type": "string", "required": True}
                ],
                "outputs": [
                    {"name": "result", "type": "string"}
                ]
            }
        }
        edit_res = self.client.EditOperator(edit_data, Headers)
        assert edit_res[0] == 200
        assert edit_res[1]["version"] != v1
        assert edit_res[1]["status"] == "unpublish" # 默认为未发布

    @allure.title("注册函数算子，缺少必填字段code，注册失败")
    def test_register_function_operator_invalid(self, Headers):
        data = {
            "operator_metadata_type": "function",
            "function_input": {
                "name": "invalid_func",
                "script_type": "python"
                # 缺少 code
            }
        }
        result = self.client.RegisterOperator(data, Headers)
        # 后端可能会返回 400 或 200带failed，取决于具体校验点
        assert result[0] in [400, 200]
        if result[0] == 200:
            assert result[1][0]["status"] == "failed"
