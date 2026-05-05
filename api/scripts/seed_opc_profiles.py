"""一次性脚本：向 opc_profiles 表插入 7 个匹配聊天提示标签的 OPC 画像"""

import sys
import os

# 确保 api 目录在 path 中
_api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _api_dir)

from db.supabase import get_supabase

PROFILES = [
    {
        "name": "陈明远",
        "role": "AI 应用开发工程师",
        "description": "专注智能客服与 NLP 对话系统，3 年 AI 产品落地经验。做过金融、教育行业的 FAQ 机器人，日处理咨询 2000+。熟悉主流大模型接入与企业 IM 集成。",
        "skills": "Python,OpenAI API,对话系统,NLP,LangChain,企业微信/钉钉集成,FastAPI,RAG",
        "is_available": True,
    },
    {
        "name": "林晓薇",
        "role": "跨境电商独立站开发者",
        "description": "5 年跨境电商建站经验，服务过 30+ 出海品牌。擅长 Shopify/WooCommerce 定制开发，从建站到支付物流全链路打通，熟悉欧美和东南亚市场。",
        "skills": "Shopify,WooCommerce,SEO,支付集成,多语言,Facebook广告,Google Analytics,物流对接",
        "is_available": True,
    },
    {
        "name": "王浩然",
        "role": "数据可视化工程师",
        "description": "前大厂 BI 工程师，专注经营数据看板与决策支持系统。帮多家中小企业搭建实时数据大屏，让老板一部手机看懂生意。擅长大屏、报表、自动化数据 pipeline。",
        "skills": "React,ECharts,SQL,Metabase,Superset,数据仓库,Python,自动化ETL",
        "is_available": True,
    },
    {
        "name": "赵雨晴",
        "role": "品牌设计师",
        "description": "独立品牌设计师，7 年从业经验。专注一人公司/初创品牌的 VI 全案设计，从 Logo 到包装到社交媒体视觉，让品牌一眼被记住。合作过餐饮、教育、消费品等领域。",
        "skills": "Figma,Brand Design,VI设计,Logo设计,插画,包装设计,品牌策略,Adobe Illustrator",
        "is_available": True,
    },
    {
        "name": "张磊",
        "role": "财务系统开发工程师",
        "description": "10 年企业财务系统开发经验，精通金蝶用友等主流财务软件 API 对接。专做自动化对账、费用报销、财务报表自动化，帮企业省掉 80% 手工操作。",
        "skills": "Python,ERP,金蝶用友API,自动化脚本,Excel VBA,MySQL,财务流程,发票识别OCR",
        "is_available": True,
    },
    {
        "name": "何思远",
        "role": "小程序全栈开发",
        "description": "专注微信生态 4 年，交付 50+ 小程序项目。从商城、预约系统到工具类应用，做过餐饮、零售、家政等多行业。熟悉支付、会员、营销插件全套方案。",
        "skills": "微信小程序,UniApp,Vue.js,微信支付,云开发,SCRM,Node.js,MySQL",
        "is_available": True,
    },
    {
        "name": "苏婉清",
        "role": "短视频内容策划",
        "description": "前 MCN 内容总监，现独立服务一人公司和中小企业。专注获客型短视频内容矩阵——从账号定位、脚本策划到投放优化，帮客户从 0 做到月均精准线索 200+。",
        "skills": "短视频脚本,剪映,内容策略,账号运营,私域引流,数据分析,投放优化,口播文案",
        "is_available": True,
    },
]


def main():
    client = get_supabase()

    for p in PROFILES:
        try:
            resp = client.table("opc_profiles").insert(p).execute()
            inserted = resp.data[0] if resp.data else None
            print(f"✓ {p['name']} ({p['role']}) → id={inserted['id'] if inserted else 'FAILED'}")
        except Exception as e:
            print(f"✗ {p['name']} 插入失败: {e}")

    print(f"\n完成，共插入 {len(PROFILES)} 条 OPC 画像。")


if __name__ == "__main__":
    main()
