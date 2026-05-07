"""知识图谱 —— 领域-技能-项目类型的关联推理"""

from typing import List, Dict, Any, Optional

# ═══════════════════════════════════════════════════════
# 领域 → 技能 映射
# ═══════════════════════════════════════════════════════

DOMAIN_SKILL_MAP: Dict[str, List[str]] = {
    "电商": ["电商平台开发", "支付集成", "商品管理", "订单系统", "营销工具"],
    "教育": ["在线教学平台", "直播授课", "题库系统", "学习管理", "视频点播"],
    "金融": ["交易系统", "风控引擎", "数据安全", "合规审计", "支付结算"],
    "医疗": ["电子病历", "预约挂号", "在线问诊", "HIS系统", "数据隐私"],
    "企业服务": ["OA系统", "ERP系统", "CRM系统", "流程自动化", "数据报表"],
    "社交": ["IM即时通讯", "社区运营", "UGC内容管理", "推荐算法", "实时消息"],
    "AI/智能": ["自然语言处理", "机器学习", "计算机视觉", "知识图谱", "推荐系统"],
    "游戏": ["Unity/Unreal", "游戏引擎", "3D建模", "物理引擎", "多人联机"],
    "物联网": ["嵌入式开发", "传感器", "MQTT协议", "设备管理", "边缘计算"],
    "区块链": ["智能合约", "共识算法", "DApp开发", "DeFi", "NFT"],
    "内容/媒体": ["CMS系统", "视频处理", "流媒体", "CDN加速", "SEO优化"],
    "零售": ["POS系统", "进销存", "会员管理", "数据分析", "全渠道"],
    "餐饮": ["点餐系统", "排队叫号", "后厨管理", "外卖对接", "会员营销"],
    "出行": ["地图导航", "实时调度", "轨迹追踪", "计费系统", "LBS服务"],
}

# ═══════════════════════════════════════════════════════
# 关键词 → 领域 反向映射
# ═══════════════════════════════════════════════════════

KEYWORD_DOMAIN_MAP: Dict[str, str] = {
    # 电商相关
    "电商": "电商", "购物": "电商", "商品": "电商", "订单": "电商",
    "支付": "金融", "微信支付": "电商", "支付宝": "电商",
    # 教育相关
    "教育": "教育", "培训": "教育", "学习": "教育", "课程": "教育",
    "直播课": "教育", "题库": "教育",
    # 金融相关
    "交易": "金融", "风控": "金融", "银行": "金融", "证券": "金融",
    "理财": "金融", "保险": "金融",
    # 医疗相关
    "医疗": "医疗", "医院": "医疗", "挂号": "医疗", "问诊": "医疗",
    "病历": "医疗", "HIS": "医疗",
    # 企业服务
    "OA": "企业服务", "OA系统": "企业服务", "ERP": "企业服务", "CRM": "企业服务",
    "审批": "企业服务", "考勤": "企业服务", "企业": "企业服务",
    # AI
    "AI": "AI/智能", "人工智能": "AI/智能", "机器学习": "AI/智能",
    "NLP": "AI/智能", "客服": "AI/智能", "智能客服": "AI/智能",
    "大模型": "AI/智能", "自然语言": "AI/智能",
    # 小程序/App
    "小程序": "电商", "微信小程序": "电商", "App": "电商",
    "公众号": "内容/媒体",
    # 直播
    "直播": "电商", "视频": "内容/媒体", "短视频": "内容/媒体",
    "内容": "内容/媒体", "媒体": "内容/媒体",
    # 系统/网站
    "网站": "企业服务", "系统": "企业服务",
    "管理": "企业服务", "后台": "企业服务",
}

# ═══════════════════════════════════════════════════════
# 项目类型 → 典型属性
# ═══════════════════════════════════════════════════════

PROJECT_TYPE_ATTRS: Dict[str, Dict[str, Any]] = {
    "AI客服": {
        "domain": "AI/智能",
        "typical_skills": ["自然语言处理", "Python", "对话系统", "知识库"],
        "typical_budget": {"min": 100000, "max": 300000},
        "typical_timeline": "2-3个月",
        "complexity": "medium",
    },
    "电商平台": {
        "domain": "电商",
        "typical_skills": ["Java", "SpringBoot", "Vue.js", "MySQL", "支付集成"],
        "typical_budget": {"min": 150000, "max": 500000},
        "typical_timeline": "3-6个月",
        "complexity": "high",
    },
    "小程序": {
        "domain": "电商",
        "typical_skills": ["微信小程序", "JavaScript", "云开发", "支付"],
        "typical_budget": {"min": 50000, "max": 200000},
        "typical_timeline": "1-2月",
        "complexity": "low",
    },
    "数据看板": {
        "domain": "企业服务",
        "typical_skills": ["Python", "ECharts", "SQL", "数据分析"],
        "typical_budget": {"min": 50000, "max": 150000},
        "typical_timeline": "1-2月",
        "complexity": "low",
    },
    "网站建设": {
        "domain": "企业服务",
        "typical_skills": ["React", "Vue.js", "Node.js", "UI设计"],
        "typical_budget": {"min": 30000, "max": 100000},
        "typical_timeline": "1个月",
        "complexity": "low",
    },
    "品牌设计": {
        "domain": "内容/媒体",
        "typical_skills": ["品牌设计", "VI设计", "UI/UX", "平面设计"],
        "typical_budget": {"min": 5000, "max": 50000},
        "typical_timeline": "2-4周",
        "complexity": "low",
    },
    "财务系统": {
        "domain": "金融",
        "typical_skills": ["Java", "Oracle", "财务知识", "数据安全"],
        "typical_budget": {"min": 200000, "max": 1000000},
        "typical_timeline": "3-6个月",
        "complexity": "high",
    },
    "短视频": {
        "domain": "内容/媒体",
        "typical_skills": ["视频剪辑", "After Effects", "内容策划", "拍摄"],
        "typical_budget": {"min": 3000, "max": 30000},
        "typical_timeline": "按条计",
        "complexity": "low",
    },
    "跨境电商": {
        "domain": "电商",
        "typical_skills": ["多语言开发", "跨境支付", "国际物流", "SEO"],
        "typical_budget": {"min": 100000, "max": 400000},
        "typical_timeline": "2-4个月",
        "complexity": "medium",
    },
}


def infer_domain_from_keywords(text: str) -> Dict[str, Any]:
    """从文本关键词推断领域"""
    scores: Dict[str, float] = {}

    for keyword, domain in KEYWORD_DOMAIN_MAP.items():
        if keyword.lower() in text.lower():
            scores[domain] = scores.get(domain, 0) + 1

    if not scores:
        return {"value": "企业服务", "confidence": 0.3, "alternatives": []}

    total = sum(scores.values())
    scored = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return {
        "value": scored[0][0],
        "confidence": min(0.8, scored[0][1] / total),
        "alternatives": [d for d, _ in scored[1:4]],
    }


def infer_from_project_type(project_type: str) -> Dict[str, Any]:
    """根据项目类型推断领域、技能、预算、工期"""
    attrs = PROJECT_TYPE_ATTRS.get(project_type)
    if not attrs:
        # 模糊匹配
        for key, val in PROJECT_TYPE_ATTRS.items():
            if key in project_type or project_type in key:
                return {
                    "domain": val["domain"],
                    "skills": val["typical_skills"],
                    "budget": val["typical_budget"],
                    "timeline": val["typical_timeline"],
                    "complexity": val["complexity"],
                    "confidence": 0.6,
                    "source": "knowledge_graph",
                }
        return {"confidence": 0.0, "source": "knowledge_graph"}

    return {
        "domain": attrs["domain"],
        "skills": attrs["typical_skills"],
        "budget": attrs["typical_budget"],
        "timeline": attrs["typical_timeline"],
        "complexity": attrs["complexity"],
        "confidence": 0.75,
        "source": "knowledge_graph",
    }


def get_related_skills(domain: str, project_type: str = "") -> List[str]:
    """获取领域相关的技能列表"""
    skills = DOMAIN_SKILL_MAP.get(domain, [])
    if project_type:
        attrs = PROJECT_TYPE_ATTRS.get(project_type, {})
        type_skills = attrs.get("typical_skills", [])
        # 合并去重
        seen = set(skills)
        skills = skills + [s for s in type_skills if s not in seen]
    return skills
