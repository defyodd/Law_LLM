import os
import json
from utils import fetch_html_with_selenium
from law_parser import parse_law_articles

# 分类对应文件
categories = {
    # "civil_code": "urls/civil_code.txt",    #民法典
    #  "penal_code": "urls/penal_code.txt",    #刑法    
    # "punish_law": "urls/punish_law.txt",    #治安管理处罚法
    # "constitution": "urls/constitution.txt",    #宪法
    # "supervision_law":"urls/supervision_law.txt" ,   #监察法
    # "company_law" : "urls/company_law.txt",    #公司法
    # "relics_protection_law": "urls/relics_protection_law.txt",   #文物保护法
    # "legislation_law": "urls/legislation_law.txt",  #立法法
    # "tax_law": "urls/tax_law.txt",   #税法
    # "account_law": "urls/account_law.txt" ,  # 会计法
    # "labor_law": "urls/labor_law.txt" ,  # 劳动法
    # "antitrust_law": "urls/antitrust_law.txt" ,  #反垄断法
    # "national_defense_edu_law": "urls/national_defense_law.txt" ,  #国防教育法
    # "national_defense_law": "urls/national_defense_law.txt" ,  #国防法
    # "compulsory_edu_law": "urls/compulsory_edu_law.txt",  #义务教育法
    # "minors_protection_law": "urls/minors_protection_law.txt" ,  #未成年人保护法
    # "charity_law": "urls/charity_law.txt",  #慈善法
    # "women_rights_law": "urls/women_rights_law.txt",  #妇女权益保障法法
    # "anti_espionage_Law": "urls/anti_espionage_law.txt",    #反间谍法
    # "civil_procedure_law": "urls/civil_procedure_law.txt",  #民事诉讼法
    # "criminal_procedure_law": "urls/criminal_procedure_law.txt",  #刑事诉讼法
    # "beijing_wildanimal_protection_law": "urls/beijing_wildanimal_protection_law.txt" ,   #北京野生动物保护条例
    "land_administration_law": "urls/land_administration_law.txt",  #土地管理法
    "environmental_protection_law": "urls/environmental_protection_law.txt",  #环境保护法
    "Anti-Unfair_Competition_Law": "urls/anti_unfair_competition_law.txt",  #反不正当竞争法
    "infectious_disease_prevention_law":"urls/infectious_disease_prevention_law.txt",   #传染病防治法
    "foreign_relations_law": "urls/foreign_relations_law.txt",   #对外关系法
    "patriotic_education_law": "urls/patriotic_education_law.txt"  , #爱国主义教育法 
    "banking_law": "urls/banking_law.txt",   #银行业监督管理法
    "Administrative Licensing Law": "urls/administrative_licensing_law.txt",   #行政许可法
    "Government Procurement Law": "urls/government_procurement_law.txt",   #政府采购法
    "price_law": "urls/price_law.txt",   #价格法
    "Civil Servants Law": "urls/civil_servants_law.txt",    #公务员法 
    "Budget_Law": "urls/budget_law.txt" , #预算法
    "Administrative Punishment Law": "urls/administrative_punishment_law.txt"  ,  #行政处罚法
    "Urban and Rural Planning Law": "urls/urban_and_rural_planning_law.txt"  , #城乡规划法
    "Production Safety Law": "urls/production_safety_law.txt",  #生产安全法
    "Securities Investment Fund Law": "urls/securities_investment_fund_law.txt",  #证券投资基金法
    "insurance_law": "urls/insurance_law.txt",  #保险法
    "Labor Contract Law": "urls/labor_contract_law.txt",  #劳动合同法
    "Construction Law": "urls/construction_law.txt",  #建筑法
    "water_law": "urls/water_law.txt",  #水法
    "Soil and Water Conservation Law": "urls/soil_and_water_conservation_law.txt",  #水土保持法
    "water_pollution_prevention_law": "urls/water_pollution_prevention_law.txt",  #水污染防治法
    "air_pollution_prevention_law": "urls/air_pollution_prevention_law.txt",  #大气污染防治法
    "Administrative Compulsion Law": "urls/administrative_compulsion_law.txt",  #行政强制法
    "Securities Law": "urls/securities_law.txt",  #证券法
    "Pharmaceutical Administration Law": "urls/pharmaceutical_administration_law.txt",  #药品管理法
    "Food Safety Law": "urls/food_safety_law.txt",  #食品安全法
    "Rural Land Contracting Law": "urls/rural_land_contracting_law.txt", #农村土地承包法
    "Flood Control Law": "urls/flood_control_law.txt", #防洪法
    "Forest Law": "urls/forest_law.txt", #森林法
    "Grassland Law": "urls/grassland_law.txt", #草原法
    "Fisheries Law": "urls/fisheries_law.txt", #渔业法
    "Mineral Resources Law": "urls/mineral_resources_law.txt", #矿产资源法
    "Coal Law": "urls/coal_law.txt", #煤炭法
    "Electric Power Law": "urls/electric_power_law.txt", #电力法

    # 可继续添加更多
}

def read_urls(filepath):
    with open(filepath, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_json(data, category):
    law_title = category.replace("_", " ").title()
    # save_dir = os.path.join("data", category)
    # os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join("data", f"{law_title}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f" 已保存：{filename}")

def main():
    for category, url_file in categories.items():
        print(f"\n📂 正在处理分类：{category}")
        urls = read_urls(url_file)
        for url in urls:
            print(f"🌐 爬取：{url}")
            try:
                html = fetch_html_with_selenium(url)
                law_data = parse_law_articles(html)
                save_json(law_data, category)
            except Exception as e:
                print(f" 出错：{e}")
                import traceback
                print(traceback.format_exc())

if __name__ == "__main__":
    main()

