import json
from typing import List, Dict, Optional
from openai import OpenAI


class ContractAgent:
    def __init__(self, api_key: str = 'sk-de88dee6506d49c59ccaecb8abd91045', model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []

        # 初始化 DeepSeek 客户端
        if api_key:
            self.llm = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.llm = None

    def _call_llm_api(self, messages: List[Dict]) -> str:
        """调用 DeepSeek API"""
        if not self.llm:
            return "请配置 DeepSeek API 密钥以启用智能功能"

        try:
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用 DeepSeek API 失败: {e}")
            return "抱歉，AI 服务暂时不可用，请稍后重试。"

    # 其他方法保持不变...
    def answer(self, question: str, history: List[Dict] = None, context_chats: list = None) -> dict:
        # 更新对话历史
        if history:
            self.conversation_history = history

        # 检测是否为制作合同相关问题
        contract_creation_keywords = ["制作", "起草", "拟定", "编写", "撰写", "合同模板", "合同范本", "生成", "修改",
                                      "完善"]

        # 定义合同模板
        contract_templates = {
            "租赁合同": self._generate_lease_contract,
            "买卖合同": self._generate_sales_contract,
            "借款合同": self._generate_loan_contract,
            "劳动合同": self._generate_labor_contract,
            "服务合同": self._generate_service_contract
        }

        is_contract_creation = any(kw in question for kw in contract_creation_keywords)
        contract_type = next((ct for ct in contract_templates.keys() if ct in question), None)

        # 检查是否是对已生成合同的修改请求
        is_modification = self._is_contract_modification(question)

        if is_contract_creation or any(kw in question for kw in ["合同", "协议"]) or is_modification:
            if is_modification and self.conversation_history:
                # 处理合同修改请求
                return self._handle_contract_modification(question)
            elif contract_type:
                # 使用大模型生成个性化合同
                return self._generate_smart_contract(question, contract_type, context_chats)
            else:
                # 使用大模型理解用户需求
                return self._understand_contract_needs(question, context_chats)

        return {
            "agent": "ContractAgent",
            "answer": "我专门处理法律合同生成和修改，请说明您需要生成或修改的合同类型。",
            "confidence": 0.4,
            "suggestions": ["请明确合同生成需求"],
            "relevant_articles": [],
            "query_type": "其他",
            "keywords": [],
            "type": "chat"
        }

    def _is_contract_modification(self, question: str) -> bool:
        """检测是否为合同修改请求"""
        modification_keywords = ["修改", "调整", "更改", "完善", "补充", "删除", "替换"]
        return any(kw in question for kw in modification_keywords)

    def _handle_contract_modification(self, question: str) -> dict:
        """处理合同修改请求"""
        # 从历史记录中找到最近的合同内容
        last_contract = None
        for msg in reversed(self.conversation_history):
            if isinstance(msg, dict) and msg.get("contract_content"):
                last_contract = msg["contract_content"]
                break

        if not last_contract:
            return {
                "agent": "ContractAgent",
                "answer": "没有找到需要修改的合同内容，请先生成一份合同。",
                "confidence": 0.6,
                "suggestions": ["请先生成合同模板"],
                "relevant_articles": [],
                "query_type": "合同修改",
                "keywords": [],
                "type": "chat"
            }

        # 使用大模型处理修改请求
        modified_contract = self._modify_contract_with_ai(last_contract, question)

        return {
            "agent": "ContractAgent",
            "answer": f"已根据您的要求修改合同：\n\n{modified_contract}",
            "confidence": 0.9,
            "suggestions": [
                "请检查修改是否符合您的需求",
                "如需进一步调整，请继续说明",
                "建议法律专业人士审核后使用"
            ],
            "relevant_articles": ["《民法典》第三编 合同"],
            "query_type": "合同修改",
            "keywords": ["修改合同"],
            "contract_content": modified_contract,
            "type": "write"
        }

    def _generate_smart_contract(self, question: str, contract_type: str, context_chats: list = None) -> dict:
        """使用大模型生成个性化合同"""
        # 获取基础模板
        contract_templates = {
            "租赁合同": self._generate_lease_contract,
            "买卖合同": self._generate_sales_contract,
            "借款合同": self._generate_loan_contract,
            "劳动合同": self._generate_labor_contract,
            "服务合同": self._generate_service_contract
        }

        base_template = contract_templates[contract_type]()

        # 使用大模型根据用户需求定制合同
        customized_contract = self._customize_contract_with_ai(base_template, question, contract_type, context_chats)

        return {
            "agent": "ContractAgent",
            "answer": f"已为您生成定制化的{contract_type}：\n\n{customized_contract}",
            "confidence": 0.95,
            "suggestions": [
                "请根据实际情况修改当事人信息",
                "如需调整条款，请告诉我具体要求",
                "建议法律专业人士审核后使用"
            ],
            "relevant_articles": ["《民法典》第三编 合同", "《民法典》第四百六十四条"],
            "query_type": "合同生成",
            "keywords": ["生成合同", contract_type],
            "contract_content": customized_contract,
            "type": "write"
        }

    def _understand_contract_needs(self, question: str, context_chats: list = None) -> dict:
        """使用大模型理解用户合同需求"""
        ai_response = self._call_ai_for_understanding(question, context_chats)

        return {
            "agent": "ContractAgent",
            "answer": ai_response,
            "confidence": 0.8,
            "suggestions": ["请提供更多具体信息以生成精确的合同"],
            "relevant_articles": [],
            "query_type": "需求理解",
            "keywords": ["合同咨询"],
            "type": "chat"
        }

    def _call_ai_for_understanding(self, question: str, context_chats: list = None) -> str:
        """调用大模型理解用户需求"""
        system_msg = """你是一个专业的法律合同助手。你的任务是：
1. 理解用户的合同需求
2. 询问必要的细节信息
3. 推荐合适的合同类型
4. 提供专业的法律建议

可生成的合同类型：租赁合同、买卖合同、借款合同、劳动合同、服务合同

请用中文回复，语言专业且易懂。"""

        try:
            messages = [{"role": "system", "content": system_msg}]
            
            # 添加上下文对话记录
            if context_chats:
                for chat in context_chats:
                    if chat.prompt and chat.answer:
                        messages.append({"role": "user", "content": chat.prompt})
                        messages.append({"role": "assistant", "content": chat.answer})
            
            # 如果没有数据库上下文，使用内存中的历史记录作为后备
            elif self.conversation_history:
                messages.extend(self.conversation_history)
            
            # 添加当前问题
            messages.append({"role": "user", "content": question})

            response = self._call_llm_api(messages)
            return response
        except Exception as e:
            return f"我可以为您生成以下类型的专业法律合同：\n• 租赁合同\n• 买卖合同\n• 借款合同\n• 劳动合同\n• 服务合同\n\n请明确您需要哪种类型的合同，以及具体的使用场景。"

    def _customize_contract_with_ai(self, base_template: str, question: str, contract_type: str, context_chats: list = None) -> str:
        """使用大模型定制合同内容"""
        system_msg = f"""你是一个专业的法律合同起草助手。请根据用户需求，对以下{contract_type}模板进行定制化修改：

基础模板：
{base_template}

要求：
1. 保持合同的法律有效性
2. 根据用户具体需求调整条款
3. 确保格式专业规范
4. 保留必要的法律条款
5. 使用规范的中文法律术语

请直接返回修改后的完整合同内容，不要添加额外说明。"""

        try:
            messages = [{"role": "system", "content": system_msg}]
            
            # 添加上下文对话记录
            if context_chats:
                for chat in context_chats:
                    if chat.prompt and chat.answer:
                        messages.append({"role": "user", "content": chat.prompt})
                        messages.append({"role": "assistant", "content": chat.answer})
            
            # 添加当前问题
            messages.append({"role": "user", "content": f"请根据以下需求定制合同：{question}"})

            response = self._call_llm_api(messages)
            return response if response else base_template
        except Exception as e:
            return base_template

    def _modify_contract_with_ai(self, contract_content: str, modification_request: str) -> str:
        """使用大模型修改合同"""
        system_msg = """你是一个专业的法律合同修改助手。请根据用户要求修改合同内容，确保：
1. 修改后的合同仍具有法律有效性
2. 保持合同格式的专业性
3. 只修改用户指定的部分
4. 保留重要的法律条款
5. 使用规范的中文法律术语

请直接返回修改后的完整合同内容，不要添加额外说明。"""

        try:
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"原合同内容：\n{contract_content}\n\n修改要求：{modification_request}"}
            ]

            response = self._call_llm_api(messages)
            return response if response else contract_content
        except Exception as e:
            return contract_content

    # 保留原有的合同模板方法...
    def _generate_lease_contract(self) -> str:
        return """# 房屋租赁合同

## 合同双方

**甲方（出租方）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

**乙方（承租方）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

根据《民法典》相关规定，甲乙双方在平等自愿基础上达成如下协议：

## 第一条 租赁房屋情况
- **房屋地址：** _____________________
- **建筑面积：** _____________________
- **房屋用途：** _____________________

## 第二条 租赁期限
自____年____月____日起至____年____月____日止。

## 第三条 租金及支付方式
- **月租金：** 人民币____元
- **支付方式：** _____________________

## 第四条 押金
**押金金额：** 人民币____元

## 第五条 双方权利义务
甲方应保证房屋符合居住条件，乙方应按时支付租金并合理使用房屋。

## 第六条 违约责任
任何一方违约，应承担相应法律责任。

## 第七条 争议解决
本合同争议由房屋所在地法院管辖。

---

**甲方签字：** _______________  **日期：** _______________  
**乙方签字：** _______________  **日期：** _______________"""

    def _generate_sales_contract(self) -> str:
        """生成买卖合同模板"""
        return """# 买卖合同

## 合同双方

**甲方（出卖人）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

**乙方（买受人）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

根据《民法典》相关规定，甲乙双方在平等自愿基础上达成如下协议：

## 第一条 标的物
- **商品名称：** _____________________
- **规格型号：** _____________________
- **数量：** _____________________
- **质量标准：** _____________________

## 第二条 价款及支付方式
- **总价款：** 人民币____元
- **支付方式：** _____________________
- **支付时间：** _____________________

## 第三条 交付
- **交付时间：** _____________________
- **交付地点：** _____________________
- **运输方式：** _____________________

## 第四条 质量保证
甲方保证所售商品符合约定的质量标准。

## 第五条 违约责任
任何一方违约，应承担相应法律责任并赔偿损失。

## 第六条 争议解决
本合同争议由合同签订地法院管辖。

---

**甲方签字：** _______________  **日期：** _______________  
**乙方签字：** _______________  **日期：** _______________"""

    def _generate_loan_contract(self) -> str:
        """生成借款合同模板"""
        return """# 借款合同

## 合同双方

**甲方（贷款人）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

**乙方（借款人）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

根据《民法典》相关规定，甲乙双方在平等自愿基础上达成如下协议：

## 第一条 借款金额
**借款金额：** 人民币____元（大写：____）

## 第二条 借款期限
自____年____月____日起至____年____月____日止。

## 第三条 利率及利息
- **年利率：** ____%
- **利息计算方式：** _____________________
- **利息支付时间：** _____________________

## 第四条 还款方式
**还款方式：** _____________________

## 第五条 担保
**担保方式：** _____________________

## 第六条 违约责任
乙方逾期还款的，应按日加收逾期利息。

## 第七条 争议解决
本合同争议由贷款人住所地法院管辖。

---

**甲方签字：** _______________  **日期：** _______________  
**乙方签字：** _______________  **日期：** _______________"""

    def _generate_labor_contract(self) -> str:
        """生成劳动合同模板"""
        return """# 劳动合同

## 合同双方

**甲方（用人单位）：** _______________  
**地址：** _____________________  
**法定代表人：** _____________________  

**乙方（劳动者）：** _______________  
**身份证号：** _____________________  
**住址：** _____________________  

根据《劳动法》、《劳动合同法》等相关规定，甲乙双方达成如下协议：

## 第一条 合同期限
- **合同类型：** _____________________
- **合同期限：** 自____年____月____日起至____年____月____日止

## 第二条 工作内容和地点
- **工作岗位：** _____________________
- **工作地点：** _____________________
- **工作内容：** _____________________

## 第三条 工作时间和休息休假
- **工作时间：** 每日____小时，每周____小时
- **休息日：** _____________________

## 第四条 劳动报酬
- **基本工资：** 人民币____元/月
- **工资支付日：** 每月____日

## 第五条 社会保险
甲方依法为乙方缴纳社会保险费。

## 第六条 劳动纪律
乙方应遵守甲方依法制定的规章制度。

## 第七条 合同解除
按照《劳动合同法》相关规定执行。

---

**甲方盖章：** _______________  **日期：** _______________  
**乙方签字：** _______________  **日期：** _______________"""

    def _generate_service_contract(self) -> str:
        """生成服务合同模板"""
        return """# 服务合同

## 合同双方

**甲方（委托方）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

**乙方（服务方）：** _______________  
**地址：** _____________________  
**电话：** _____________________  

根据《民法典》相关规定，甲乙双方在平等自愿基础上达成如下协议：

## 第一条 服务内容
- **服务项目：** _____________________
- **服务标准：** _____________________
- **服务期限：** _____________________

## 第二条 服务费用
- **服务费用：** 人民币____元
- **支付方式：** _____________________
- **支付时间：** _____________________

## 第三条 双方权利义务
- **甲方义务：** 配合乙方提供服务，按时支付费用
- **乙方义务：** 按约定标准提供服务

## 第四条 服务质量
乙方应保证服务质量符合约定标准。

## 第五条 知识产权
**知识产权归属：** _____________________

## 第六条 违约责任
任何一方违约，应承担相应法律责任。

## 第七条 争议解决
本合同争议由合同履行地法院管辖。

---

**甲方签字：** _______________  **日期：** _______________  
**乙方签字：** _______________  **日期：** _______________"""