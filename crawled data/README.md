# 法律条文爬虫项目

## 项目简介
本项目旨在从北大法宝网站爬取各类法律条文，包括民法典、刑法、治安管理处罚法等，并将其保存为JSON格式文件。

## 环境要求
- Python 3.x
- Selenium
- BeautifulSoup
- Microsoft Edge 浏览器（用于Selenium）
- msedgedriver.exe（与Edge浏览器版本匹配）

## 依赖安装
1. 安装Selenium：`pip install selenium`
2. 安装BeautifulSoup：`pip install beautifulsoup4`
3. 确保已安装Microsoft Edge浏览器，并下载对应版本的[msedgedriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)。

## 代码结构说明
- **utils.py**：包含使用Selenium抓取网页HTML的函数。
- **law_parser.py**：解析HTML中的法律条文，并将其转换为结构化数据。
- **spider.py**：主程序，负责读取URL、调用解析器并保存结果。
- **urls/**：存放各类法律条文页面的URL。
- **data/**：存放爬取并解析后的法律条文JSON文件。

## 使用步骤
1. 配置urls目录下的.txt文件，确保其中的URL正确无误。
2. 运行spider.py：`python spider.py`
3. 爬取的数据将保存在data目录下。

## 数据处理流程

### 输入
- **URL文件**：位于urls目录下的.txt文件，每行包含一个法律条文页面的URL。

### 处理流程
1. **抓取网页**：使用Selenium从指定URL抓取网页HTML内容。
2. **解析HTML**：利用BeautifulSoup解析HTML，提取法律标题和条文内容。
3. **保存JSON**：将解析后的数据以JSON格式保存至data目录下。

### 输出
- **data文件夹**：存放爬取并解析后的法律条文JSON文件。
- **JSON文件**：每个法律条文对应一个JSON文件，包含标题和条文内容。
- **JSON格式**：
```json
{
  "title": "中华人民共和国民法典",
  "parts": [
    {
      "part_title": "第一编　总则",
      "subparts": [],
      "chapters": [
        {
          "chapter_title": "第一章　基本规定",
          "articles": [
            {
              "article_no": "第一条",
              "article_content": "为了保护民事主体的合法权益，调整民事关系，维护社会和经济秩序，适应中国特色社会主义发展要求，弘扬社会主义核心价值观，根据宪法，制定本法。"
            }
            ]
            }   
        ]
    }
  ]
}             
```

## 项目爬取示例
1. "civil_code": "urls/civil_code.txt",    #民法典
2. "penal_code": "urls/penal_code.txt",    #刑法    
3. "punish_law": "urls/punish_law.txt",    #治安管理处罚法
4. "constitution": "urls/constitution.txt",    #宪法
5. "supervision_law":"urls/supervision_law.txt" ,   #监察法
6. "company_law" : "urls/company_law.txt",    #公司法
7. "relics_protection_law": "urls/relics_protection_law.txt",   #文物保护法
8. "legislation_law": "urls/legislation_law.txt",  #立法法
9. "tax_law": "urls/tax_law.txt",   #税法
10. "account_law": "urls/account_law.txt" ,  # 会计法
11. "labor_law": "urls/labor_law.txt" ,  # 劳动法
12. "antitrust_law": "urls/antitrust_law.txt" ,  #反垄断法
13. "national_defense_edu_law": "urls/national_defense_law.txt" ,  #国防教育法
14. "national_defense_law": "urls/national_defense_law.txt" ,  #国防法
15. "compulsory_edu_law": "urls/compulsory_edu_law.txt",  #义务教育
16. "minors_protection_law": "urls/minors_protection_law.txt" ,  #未成年人保护法
17. "charity_law": "urls/charity_law.txt",  #慈善法
18. "women_rights_law": "urls/women_rights_law.txt",  #妇女权益保障法法
19. "anti_espionage_Law": "urls/anti_espionage_law.txt",    #反间谍法
20. "civil_procedure_law": "urls/civil_procedure_law.txt",  #民事诉讼法
21. "criminal_procedure_law": "urls/criminal_procedure_law.txt",  #刑事诉讼法
22. "beijing_wildanimal_protection_law": "urls/beijing_wildanimal_protection_law.txt"    #北京野生动物保护条例
23. "land_administration_law": "urls/land_administration_law.txt",  #土地管理法
24. "environmental_protection_law": "urls/environmental_protection_law.txt",  #环境保护法
25. "Anti-Unfair_Competition_Law": "urls/anti_unfair_competition_law.txt",  #反不正当竞争法
26. "infectious_disease_prevention_law":"urls/infectious_disease_prevention_law.txt",   #传染病防治法
27. "foreign_relations_law": "urls/foreign_relations_law.txt",   #对外关系法
28. "patriotic_education_law": "urls/patriotic_education_law.txt"  , #爱国主义教育法 
29. "banking_law": "urls/banking_law.txt",   #银行业监督管理法
30. "Administrative Licensing Law": "urls/administrative_licensing_law.txt",   #行政许可法
31. "Government Procurement Law": "urls/government_procurement_law.txt",   #政府采购法
32. "price_law": "urls/price_law.txt",   #价格法
33. "Civil Servants Law": "urls/civil_servants_law.txt",    #公务员法 
34. "Budget_Law": "urls/budget_law.txt" , #预算法
35. "Administrative Punishment Law": "urls/administrative_punishment_law.txt"  ,  #行政处罚法
36. "Urban and Rural Planning Law": "urls/urban_and_rural_planning_law.txt"  , #城乡规划法
37. "Production Safety Law": "urls/production_safety_law.txt",  #生产安全法
38. "Securities Investment Fund Law": "urls/securities_investment_fund_law.txt",  #证券投资基金法
39. "insurance_law": "urls/insurance_law.txt",  #保险法
40. "Labor Contract Law": "urls/labor_contract_law.txt",  #劳动合同法
41. "Construction Law": "urls/construction_law.txt",  #建筑法
42. "water_law": "urls/water_law.txt",  #水法
43. "Soil and Water Conservation Law": "urls/soil_and_water_conservation_law.txt",  #水土保持法
44. "water_pollution_prevention_law": "urls/water_pollution_prevention_law.txt",  #水污染防治法
45. "air_pollution_prevention_law": "urls/air_pollution_prevention_law.txt",  #大气污染防治法
46. "Administrative Compulsion Law": "urls/administrative_compulsion_law.txt",  #行政强制法
47. "Securities Law": "urls/securities_law.txt",  #证券法
48. "Pharmaceutical Administration Law": "urls/pharmaceutical_administration_law.txt",  #药品管理法
49. "Food Safety Law": "urls/food_safety_law.txt",  #食品安全法
50. "Rural Land Contracting Law": "urls/rural_land_contracting_law.txt", #农村土地承包法
51. "Flood Control Law": "urls/flood_control_law.txt", #防洪法
52. "Forest Law": "urls/forest_law.txt", #森林法
53. "Grassland Law": "urls/grassland_law.txt", #草原法
54. "Fisheries Law": "urls/fisheries_law.txt", #渔业法
55. "Mineral Resources Law": "urls/mineral_resources_law.txt", #矿产资源法
56. "Coal Law": "urls/coal_law.txt", #煤炭法
57. "Electric Power Law": "urls/electric_power_law.txt", #电力法
58. "Railway Law": "urls/railway_law.txt", #铁路法
59. "Highway Law": "urls/highway_law.txt", #公路法
60. "Port Law": "urls/port_law.txt", #港口法
61. "Civil Aviation Law": "urls/civil_aviation_law.txt", #民用航空法
62. "Energy Conservation Law": "urls/energy_conservation_law.txt", #节约能源法
63. "Renewable Energy Law": "urls/renewable_energy_law.txt", #可再生能源法
64. "Circular Economy Promotion Law": "urls/circular_economy_promotion_law.txt", #循环经济促进法
65. "Rural Revitalization Promotion Law": "urls/rural_revitalization_promotion_law.txt", #乡村振兴促进法
66. "Agriculture Law": "urls/agriculture_law.txt", #农业法
67. "Land Surveying and Mapping Law": "urls/land_surveying_and_mapping_law.txt", #测绘法
68. "Emergency Response Law": "urls/emergency_response_law.txt", #突发事件应对法
69. "Fire Protection Law": "urls/fire_protection_law.txt", #消防法
70. "Earthquake Prevention Law": "urls/earthquake_prevention_law.txt", #防震减灾法
71. "Meteorology Law": "urls/meteorology_law.txt", #气象法
72. "Tourism Law": "urls/tourism_law.txt", #旅游法
73. "Advertising Law": "urls/advertising_law.txt", #广告法
74. "computing_security_law": "urls/computing_security_law.txt",  # 网络安全法
75. "ecommerce_law": "urls/ecommerce_law.txt",  # 电子商务法
76. "teacher_law": "urls/teacher_law.txt",  # 教师法
77. "employment_service_law": "urls/employment_service_law.txt",  # 就业促进法
78. "customs_law": "urls/customs_law.txt",  # 海关法
79. "inspection_import_export_law": "urls/inspection_import_export_law.txt",  # 进出口商品检验法
80. "anti_dumping_law": "urls/anti_dumping_law.txt",  # 反倾销法
81. "anti_subsidy_law": "urls/anti_subsidy_law.txt",  # 反补贴法
82. "patent_law": "urls/patent_law.txt",    # 专利法
83. "trademark_law": "urls/trademark_law.txt",    # 商标法
84. "copyright_law": "urls/copyright_law.txt",      # 著作权法
85. "tobacco_monopoly_law": "urls/tobacco_monopoly_law.txt",  # 烟草专卖法
86. "quality_law": "urls/quality_law.txt",  # 产品质量法
87. "vehicle_purchase_tax_law": "urls/vehicle_purchase_tax_law.txt",  # 车辆购置税法
88. "grain_security_law": "urls/grain_security_law.txt",  # 粮食安全保障法
89. "data_security_law": "urls/data_security_law.txt", # 数据安全法
90. "personal_info_protection_law": "urls/personal_info_protection_law.txt",  # 个人信息保护法
91. "consumers_rights_protection_law": "urls/consumers_rights_protection_law.txt", # 消费者权益保护法
92. "black_soil_protection_law": "urls/black_soil_protection_law.txt" ,  # 黑土地保护法
93. "yellow_river_protection_law": "urls/yellow_river_protection_law.txt",  # 黄河保护法
94. "yangtze_protection_law": "urls/yangtze_protection_law.txt",  # 长江保护法
95. "metrology_law": "urls/metrology_law.txt", # 计量法
96. "hainan_ftp_law": "urls/hainan_ftp_law.txt",    # 海南自由贸易港法
97. "cyberspace_administration_law": "urls/cyberspace_administration_law.txt", # 互联网信息服务管理办法
98. "notarization_law": "urls/notarization_law.txt",  # 公证法
99. "trust_law": "urls/trust_law.txt",  # 信托法
s
## 注意事项
1. 确保网络连接正常，部分页面可能需要较长时间加载。
2. 如果遇到反爬机制，可以尝试调整fetch_html_with_selenium函数中的等待时间。
3. 在使用前请确认msedgedriver.exe路径是否正确。
4. 如需爬取其他法律条文，请添加相应的URL到urls目录下。