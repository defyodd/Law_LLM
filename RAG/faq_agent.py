class FAQAgent:
    FAQS = {
        "诉讼时效": "根据《民法典》规定，普通诉讼时效为3年，自权利人知道或应当知道权利被侵害之日起计算。",
        "离婚冷静期": "协议离婚需30天冷静期，期间任一方可撤回。",
        "劳动仲裁": "劳动争议应先申请仲裁，超过仲裁时效将影响权利主张。",
        "无效合同": "违反法律强制性规定的合同无效。",
        "担保责任": "保证人按约承担债务清偿责任。",
        "婚前财产": "婚前个人财产属个人所有，婚后不自动转为共同财产。",
        "交通肇事逃逸": "构成犯罪的将追究刑事责任，并加重处罚。",
        "精神损害赔偿": "人身权益受侵害可依法请求精神损害赔偿。",
        "继承顺序": "第一顺序：配偶、子女、父母；第二顺序：兄弟姐妹、祖父母。",
        "居住权": "自然人可享有在他人住宅中设定的居住使用权。",
        "买卖合同": "买卖合同须明确标的、数量、价格、履行方式等。",
        "违约责任": "一方违约的，应当承担继续履行、赔偿损失等责任。",
        "债权转让": "债权可依法转让，但需通知债务人。",
        "不可抗力": "指不能预见、不能避免且不能克服的客观情况。",
        "建设工程质量责任": "开发商对交付的房屋质量承担保修责任。",
        "物权变动": "物权设立、变更、转让需登记才生效。",
        "继承权放弃": "继承人可书面声明放弃继承。",
        "住房公积金提取": "购房、退休等符合条件可提取公积金。",
        "辞退赔偿": "用人单位违法解除合同须支付赔偿金。",
        "试用期": "试用期最长不超过6个月，包含在劳动合同期限内。",
        "工伤认定": "发生工伤应及时申请认定，并申请赔偿。",
        "辞职流程": "提前30日书面通知或试用期提前3日通知单位。",
        "房屋租赁合同": "应约定租金、期限、押金等，建议签署书面协议。",
        "借条有效性": "借条应载明金额、时间、借款人信息等。",
        "法人代表变更": "需办理工商变更登记，提交相应材料。",
        "公司注销": "需依法进行清算、税务注销、工商登记注销等。",
        "辞退孕妇": "用人单位不得随意解除孕期、产期女员工合同。",
        "工资支付周期": "工资应至少每月支付一次。",
        "辞职未批": "劳动者主动辞职无需单位批准。",
        "试用期解雇": "应说明理由并提前通知，否则属违法解除。",
        "工龄计算": "连续工龄影响年假、补偿金等权益。",
        "仲裁期限": "劳动争议仲裁申请时效为1年。",
        "欠薪维权": "可申请劳动监察或仲裁，依法追讨。",
        "入职未签合同": "应自用工起一个月内签订合同，否则可获双倍工资。",
        "离职证明": "单位应在离职时出具书面离职证明。",
        "档案管理": "应由人社部门或单位代管，不能私自保留。",
        "女职工三期": "怀孕、产假、哺乳期内享受法律特殊保护。",
        "公司违法裁员": "需支付赔偿金，未依法裁员可申诉。",
        "劳动报酬争议": "建议先协商，协商不成可申请仲裁。",
        "离婚房产分割": "婚后财产原则上平均分割，酌情处理。",
        "家庭暴力": "受害者可申请人身保护令，追究施暴者责任。",
        "子女抚养权": "以子女利益最大化为原则，法院综合判定。",
        "分居离婚": "分居满两年视为感情破裂可申请离婚。",
        "婚内出轨": "一般不直接影响财产分割，但可作为辅助因素。",
        "起诉离婚": "需提供证据证明感情破裂，法院判决离婚。",
        "协议离婚": "需双方同意、协议达成、登记手续完备。",
        "人身伤害赔偿": "包括医疗费、误工费、护理费等多项赔偿。",
        "交通事故赔偿": "由交警认定责任，保险先行赔偿。",
        "碰瓷责任": "可通过监控、证人举证证明非责任方。",
        "酒驾处罚": "将被罚款、扣证，严重者构成危险驾驶罪。",
        "无证驾驶": "属于违法行为，将被行政处罚甚至刑拘。",
        "车祸逃逸": "逃逸构成加重情节，可能被追究刑责。",
        "网络诈骗": "涉嫌刑事犯罪，应及时报警并收集证据。",
        "电信诈骗": "被骗后尽快拨打110或96110反诈热线。",
        "银行卡被冻结": "可能因涉嫌异常交易，应与银行或警方联系。",
        "隐私泄露": "可要求平台删除信息并赔偿损失。",
        "名誉侵权": "被诽谤、侮辱可提起民事诉讼要求赔偿。",
        "诽谤罪": "严重侵害他人名誉的，可构成刑事犯罪。",
        "图片侵权": "擅用他人图片构成侵权，应承担责任。",
        "著作权": "原创作品自动享有著作权，侵权将被追责。",
        "网络转载": "应注明来源并获得授权，避免侵权。",
        "医疗事故": "需通过鉴定程序确认责任，依法索赔。",
        "工伤赔偿": "包括医疗费、停工工资、伤残补助等。",
        "失业保险": "符合条件者可申请失业金，享受基本保障。",
        "养老保险": "累计缴满15年可领取退休金。",
        "退休年龄": "男60岁、女干部55岁、女工人50岁。",
        "社保转移": "可在新就业地申请转入原账户。",
        "公积金贷款": "需符合缴纳条件、信用状况良好。",
        "征信修复": "需由信用主体申请，不能伪造或非法代办。",
        "非法集资": "承诺高回报为特征，参与者可能承担风险。",
        "民间借贷利率": "不得超过一年期LPR的4倍，超过部分无效。",
        "信用卡逾期": "将影响征信，情节严重可构成信用卡诈骗罪。",
        "合同诈骗": "虚构合同骗取财物，属于刑事犯罪。",
        "遗产税": "目前我国未开征个人遗产税。",
        "赠与撤销": "赠与合同成立后不得任意撤销，除非受赠人重大过错。",
        "非法拘禁": "限制他人人身自由属于刑事犯罪。",
        "正当防卫": "在合法防卫限度内不负刑事责任。",
        "邻里纠纷": "应协商解决，严重的可报警或提起民事诉讼。",
        "强制执行": "法院生效判决不履行的可申请强制执行。",
        "民事调解": "法院或人民调解委员会可主持调解。",
        "违章建筑": "可依法拆除或责令改正，属行政执法事项。",
        "房产继承": "应公证或凭有效遗嘱办理继承手续。",
        "居住证": "非户籍人口在城市生活的身份证明。",
        "遗嘱有效性": "须符合形式和立遗人真实意思表示。",
        "独生子女费": "可依法领取独生子女父母奖励金。",
        "土地征收补偿": "需依照国家规定给予公平补偿。",
        "征地补偿款分配": "由村集体或村民会议讨论决定。",
        "职务犯罪举报": "可向纪委或监察部门实名举报。",
        "财产保全": "诉前/诉中可申请法院冻结对方财产。",
        "电子证据": "聊天记录、转账截图等均可作为证据提交。",
        "合同签字效力": "只要签字真实有效，合同即具约束力。",
        "银行卡盗刷": "第一时间冻结卡片并报警，银行将协助调查。",
        "信息公开": "政府部门应依法公开信息，接受公众监督。",
        "法院起诉流程": "提交起诉状，法院立案后进入审理程序。",
        "执行难": "法院执行局可申请强制执行，打击“老赖”。",
        "社区矫正": "对轻罪判缓刑人员的非监禁性监管措施。",
        "取保候审": "涉嫌犯罪但不宜羁押的，可以申请取保候审。"
    }

    def answer(self, question: str) -> dict:
        for k, v in self.FAQS.items():
            if k in question:
                return {
                    "agent": "FAQAgent",
                    "answer": v,
                    "confidence": 0.95,
                    "suggestions": ["本答复基于法律常识，如涉及个案请咨询律师"],
                    "relevant_articles": [],
                    "query_type": "常见问题",
                    "keywords": [k],
                    "type": "chat"  # 添加类型标识
                }
        return {
            "agent": "FAQAgent",
            "answer": "此问题不在常见问题库中，建议咨询其他助手。",
            "confidence": 0.2,
            "suggestions": [],
            "relevant_articles": [],
            "query_type": "未知",
            "keywords": [],
            "type": "chat"  # 添加类型标识
        }
