"""增强种子数据：每个标签类别约 10 个 OPC，共 70 个"""

import sys
import os

_api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _api_dir)

from db.supabase import get_supabase

PROFILES = [
    # ═══════════════════════════════════════════════════════
    # 1. 想用AI接住所有客户咨询 → AI/智能客服（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "陈明远",
        "role": "AI 应用开发工程师",
        "description": "专注智能客服与 NLP 对话系统，3 年 AI 产品落地经验。做过金融、教育行业的 FAQ 机器人，日处理咨询 2000+。熟悉主流大模型接入与企业 IM 集成。",
        "skills": "Python,OpenAI API,对话系统,NLP,LangChain,企业微信集成,FastAPI,RAG",
        "is_available": True,
    },
    {
        "name": "徐志豪",
        "role": "AI 客服系统架构师",
        "description": "前阿里小蜜核心开发，6 年智能客服经验。擅长多轮对话、意图识别、知识库构建，交付过电商、保险、政务等多个行业客服系统。",
        "skills": "Python,意图识别,知识图谱,DeepSeek,对话管理,Elasticsearch,多轮对话,Java",
        "is_available": True,
    },
    {
        "name": "孙雅琳",
        "role": "AI 产品经理兼开发",
        "description": "既能设计对话流程又能写代码的复合型人才。擅长把业务知识结构化，做成可被 AI 检索的知识库。帮教育、医疗行业做过智能问答系统。",
        "skills": "Python,产品设计,知识库构建,Prompt工程,向量数据库,对话设计,RAG,PostgreSQL",
        "is_available": True,
    },
    {
        "name": "刘宇飞",
        "role": "NLP 算法工程师",
        "description": "专做文本分类、情感分析、意图识别。2 年大模型微调经验，擅长用少样本让通用模型适配垂直场景。帮零售、金融客户做过智能质检和客服分析。",
        "skills": "Python,PyTorch,文本分类,情感分析,模型微调,LlamaIndex,向量搜索,HuggingFace",
        "is_available": True,
    },
    {
        "name": "周美琪",
        "role": "智能客服部署与运维",
        "description": "专注 AI 客服系统的上线部署和持续优化。精通企业微信、钉钉、飞书等多平台接入，做过 20+ 企业的客服系统落地，擅长对话效果持续调优。",
        "skills": "企业微信API,飞书集成,钉钉开发,Docker,对话分析,自动化部署,Node.js,运维",
        "is_available": True,
    },
    {
        "name": "黄凯文",
        "role": "语音客服与智能外呼开发",
        "description": "5 年语音 AI 经验，做过智能外呼、语音导航、电话客服机器人。熟悉 ASR/TTS 接入，交付过金融催收、电商回访等多种外呼场景。",
        "skills": "Python,ASR,TTS,语音合成,电话API,呼叫中心,阿里云语音,实时流处理",
        "is_available": True,
    },
    {
        "name": "钱晓东",
        "role": "大模型应用开发",
        "description": "通用大模型落地的实战派。擅长把 GPT/DeepSeek 等大模型接入实际业务流程，做客服、摘要、分析。帮多家企业用 1-2 周搭出 MVP。",
        "skills": "DeepSeek,OpenAI,Prompt工程,Agent开发,API集成,流式对话,向量数据库,数据库设计",
        "is_available": True,
    },
    {
        "name": "高思琪",
        "role": "AI 训练师与对话设计",
        "description": "不做开发，专做 AI 对话策略设计和知识库运营。帮企业梳理 FAQ、设计话术、标注数据，让机器人越用越聪明。服务过电商、医美、教育客户。",
        "skills": "对话设计,知识库运营,数据标注,话术优化,用户研究,FAQ梳理,客服流程,A/B测试",
        "is_available": True,
    },
    {
        "name": "林俊辉",
        "role": "多语言客服系统开发",
        "description": "3 年出海企业服务经验，专做中英日韩多语言 AI 客服。做过跨境电商的售前咨询机器人和售后工单系统，支持多时区多语言切换。",
        "skills": "Python,多语言NLP,翻译API,跨境电商,工单系统,React,Node.js,MongoDB",
        "is_available": True,
    },
    {
        "name": "方晓云",
        "role": "RAG 知识库工程师",
        "description": "专注检索增强生成技术，帮企业把内部文档、手册、FAQ 变成 AI 可检索的知识库。做过法律、医疗、IT 运维等专业领域的智能问答系统。",
        "skills": "RAG,Pinecone,Milvus,文档解析,语义搜索,LangChain,PDF处理,知识管理",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 2. 想把产品卖到海外去 → 跨境电商/出海（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "林晓薇",
        "role": "Shopify 独立站开发者",
        "description": "5 年跨境电商建站经验，服务过 30+ 出海品牌。擅长 Shopify 定制开发，从建站到支付物流全链路打通，熟悉欧美和东南亚市场。",
        "skills": "Shopify,WooCommerce,SEO,支付集成,多语言,Facebook广告,Google Analytics,物流对接",
        "is_available": True,
    },
    {
        "name": "郑海龙",
        "role": "亚马逊运营与站内优化",
        "description": "前 Amazon 大卖家运营总监，年 GMV 过亿。精通 Listing 优化、PPC 广告、A+ 页面设计、库存管理。帮小白卖家从 0 做到月销 10 万美金。",
        "skills": "Amazon Seller,Vendor Central,PPC广告,Keyword Research,Helium10,库存管理,竞品分析,品牌备案",
        "is_available": True,
    },
    {
        "name": "杨思颖",
        "role": "跨境独立站全栈开发",
        "description": "全栈出海开发者，既做前端商城又搭后端系统。用 Next.js + Shopify Headless 帮品牌做高性能独立站，支持多语言多币种。",
        "skills": "Next.js,Shopify Headless,多语言,多币种,SEO技术,支付网关,CDN优化,Stripe",
        "is_available": True,
    },
    {
        "name": "赵凯旋",
        "role": "TikTok Shop 运营专家",
        "description": "2 年 TikTok 电商经验，做过东南亚和英美市场。从账号冷启动到直播带货全流程，帮 10+ 品牌在 TikTok 开店并实现稳定出单。",
        "skills": "TikTok Shop,TikTok广告,短视频运营,直播带货,达人合作,内容策划,数据分析,选品策略",
        "is_available": True,
    },
    {
        "name": "沈雨桐",
        "role": "跨境品牌出海策划",
        "description": "专注 DTC 品牌出海策略，帮国内工厂和品牌从 OEM 转型自主品牌。做过户外、家居、3C 等多个品类，擅长品牌定位和社媒营销组合。",
        "skills": "品牌出海,DTC策略,市场调研,社交营销,Instagram,YouTube,PR媒体,内容营销",
        "is_available": True,
    },
    {
        "name": "马文斌",
        "role": "跨境物流与仓储顾问",
        "description": "10 年国际物流经验，精通 FBA 头程、海外仓、小包直发等各种物流方案。帮卖家优化物流成本，搭建多国仓储体系。",
        "skills": "FBA物流,海外仓,头程运输,最后一公里,库存管理,报关清关,WMS系统,供应链优化",
        "is_available": True,
    },
    {
        "name": "吴雪婷",
        "role": "Google & Meta 广告投手",
        "description": "5 年出海广告投放经验，月消耗百万美金级。精通 Google Ads、Meta Ads 全漏斗投放，擅长从测品到放量。做过服装、美妆、3C 等高竞争品类。",
        "skills": "Google Ads,Facebook Ads,GA4,Shopping广告,再营销,受众分析,落地页优化,ROI优化",
        "is_available": True,
    },
    {
        "name": "丁浩然",
        "role": "跨境 ERP 系统开发",
        "description": "专为中小卖家开发定制的跨境 ERP 系统，对接 Amazon、Shopify、Lazada、Shopee 等多平台。做订单管理、库存同步、财务报表一体化。",
        "skills": "Python,ERP开发,多平台API,订单管理,库存同步,Flask,PostgreSQL,数据同步",
        "is_available": True,
    },
    {
        "name": "许惠玲",
        "role": "跨境内容与社媒运营",
        "description": "帮出海品牌做海外社交媒体内容，从产品拍摄到英文文案到 KOL 合作一条龙。服务过 20+ 品牌，覆盖 Instagram、TikTok、Pinterest。",
        "skills": "Instagram运营,TikTok内容,英文文案,产品摄影,KOL对接,社群运营,Canva,短视频剪辑",
        "is_available": True,
    },
    {
        "name": "曹瑞阳",
        "role": "Shopee/Lazada 东南亚运营",
        "description": "3 年东南亚电商经验，深耕 Shopee 和 Lazada 平台。从选品上架到活动报名到客服售后，帮品牌快速打开印尼、泰国、菲律宾市场。",
        "skills": "Shopee运营,Lazada运营,东南亚市场,本地化,活动策划,客服管理,定价策略,多店铺管理",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 3. 想让经营数据一目了然 → 数据/BI（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "王浩然",
        "role": "数据可视化工程师",
        "description": "前大厂 BI 工程师，专注经营数据看板与决策支持系统。帮多家中小企业搭建实时数据大屏，让老板一部手机看懂生意。擅长大屏、报表、自动化数据 pipeline。",
        "skills": "React,ECharts,SQL,Metabase,Superset,数据仓库,Python,自动化ETL",
        "is_available": True,
    },
    {
        "name": "余思远",
        "role": "BI 报表开发工程师",
        "description": "7 年 BI 报表经验，精通 Tableau 和 Power BI。做过零售、制造、物流等行业的管理驾驶舱，擅长把复杂数据变成一眼能看懂的图表。",
        "skills": "Tableau,Power BI,SQL,DAX,数据建模,管理驾驶舱,报表设计,Excel高级分析",
        "is_available": True,
    },
    {
        "name": "任雅文",
        "role": "数据分析师 + 看板搭建",
        "description": "既懂分析又会搭看板的双料人才。先帮你梳理指标体系，再搭成实时数据看板。帮电商、SaaS 公司做过 GMV 监控、用户增长、留存分析看板。",
        "skills": "Python,SQL,数据指标,漏斗分析,用户增长,Superset,电商分析,留存分析",
        "is_available": True,
    },
    {
        "name": "段志强",
        "role": "数据仓库与 ETL 工程师",
        "description": "专做企业数据中台搭建，把散落在各个系统的数据汇聚清洗建模。用过阿里云、AWS、GCP 主流技术栈，帮 10+ 企业建成统一数据视图。",
        "skills": "SQL,数据仓库,ETL,AWS Redshift,dbt,Airflow,数据建模,阿里云MaxCompute",
        "is_available": True,
    },
    {
        "name": "何晓蕾",
        "role": "经营数据分析顾问",
        "description": "前管理咨询转独立顾问，专做中小企业的经营数据分析。帮你梳理关键指标、搭建分析框架、输出经营诊断报告。做过餐饮、零售、教育行业。",
        "skills": "Excel高级,商业分析,财务分析,经营管理,指标设计,数据诊断,PPT报告,业务建模",
        "is_available": True,
    },
    {
        "name": "彭宇轩",
        "role": "实时数据大屏开发",
        "description": "专注领导驾驶舱和展会大屏，3 天出 Demo 一周上线。做过双十一实时大屏、工厂生产看板、政务指挥中心大屏。前端炫技派。",
        "skills": "Three.js,D3.js,ECharts,WebSocket,实时数据,大屏适配,Canvas,动画效果",
        "is_available": True,
    },
    {
        "name": "范佳琪",
        "role": "数据产品经理兼开发",
        "description": "能独立完成从需求分析到数据看板上线的全流程。擅长把老板的需求翻译成数据产品，帮企业用数据驱动日常决策。",
        "skills": "产品设计,SQL,Metabase,数据需求分析,用户访谈,看板设计,Python,敏捷开发",
        "is_available": True,
    },
    {
        "name": "田振国",
        "role": "Python 数据分析与自动化",
        "description": "帮企业写自动化分析脚本，从数据采集到清洗到可视化报告全自动。做过每日经营日报、竞品价格监控、库存预警等自动化项目。",
        "skills": "Python,Pandas,Selenium,爬虫,自动化报表,定时任务,数据清洗,API对接",
        "is_available": True,
    },
    {
        "name": "卢晓燕",
        "role": "Excel 自动化与 VBA 开发",
        "description": "帮中小企业把 Excel 手工操作全部自动化。做过自动对账、自动生成报价单、自动汇总报表等。不需要换系统，在 Excel 里就能提效 80%。",
        "skills": "Excel VBA,宏开发,自动化模板,财务报表,Power Query,数据透视,公式优化,SQL",
        "is_available": True,
    },
    {
        "name": "姚志明",
        "role": "数据看板产品设计",
        "description": "专做数据可视化 UI 设计。让你的经营数据不光好用还好看。擅长信息架构、图表选择和交互设计，让非技术人员也能轻松看懂数据。",
        "skills": "Figma,信息架构,可视化设计,UI设计,交互设计,图表设计,看板美化,用户研究",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 4. 想让人一眼记住我的品牌 → 品牌设计/VI（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "赵雨晴",
        "role": "品牌全案设计师",
        "description": "独立品牌设计师，7 年从业经验。专注一人公司/初创品牌的 VI 全案设计，从 Logo 到包装到社交媒体视觉，让品牌一眼被记住。合作过餐饮、教育、消费品等领域。",
        "skills": "Figma,Brand Design,VI设计,Logo设计,插画,包装设计,品牌策略,Illustrator",
        "is_available": True,
    },
    {
        "name": "苏建安",
        "role": "Logo 与字体设计师",
        "description": "专做品牌 Logo 和定制字体设计，8 年经验。为 100+ 品牌设计过 Logo，拿过红点和 iF 奖。从创意概念到多场景应用，一整套交付。",
        "skills": "Logo设计,字体设计,品牌符号,创意概念,企业VI,图形设计,Adobe Creative Suite,书法设计",
        "is_available": True,
    },
    {
        "name": "杜美琳",
        "role": "电商视觉设计师",
        "description": "专做电商场景的品牌视觉，包括店铺首页、详情页、主图、活动页。帮 50+ 淘系和抖音商家做过视觉升级，转化率平均提升 30%。",
        "skills": "Photoshop,电商设计,详情页,主图设计,活动页面,视觉营销,产品精修,C4D渲染",
        "is_available": True,
    },
    {
        "name": "谢永康",
        "role": "品牌策略顾问",
        "description": "前奥美品牌策略，现独立咨询。帮你梳理品牌定位、核心价值主张、品牌故事。不是做设计，是做设计之前该想清楚的那些事。服务过科技、消费品、餐饮品牌。",
        "skills": "品牌定位,品牌策略,市场调研,用户洞察,品牌故事,品牌命名,竞品分析,品牌架构",
        "is_available": True,
    },
    {
        "name": "蔡晓萌",
        "role": "包装与印刷设计师",
        "description": "专做实体产品的包装设计，从结构到视觉到材质。做过食品、美妆、茶叶、电子产品等品类。懂印刷工艺，能帮你控制落地成本。",
        "skills": "包装设计,包装结构,印刷工艺,材质选型,刀版图,3D渲染,Illustrator,InDesign",
        "is_available": True,
    },
    {
        "name": "潘家伟",
        "role": "品牌官网设计师",
        "description": "专注品牌官网和 Landing Page 设计，让品牌在线上也有高级感。用 Webflow/Framer 直接出可上线的高保真网站，不只是设计稿。",
        "skills": "Webflow,Framer,官网设计,Landing Page,视觉设计,动效设计,响应式设计,SEO基础",
        "is_available": True,
    },
    {
        "name": "薛诗涵",
        "role": "社交媒体视觉设计",
        "description": "帮品牌做小红书、朋友圈、抖音等社交媒体的全套视觉素材。从封面到配图到信息图，让品牌日常发的内容也有统一的高级感。",
        "skills": "小红书设计,朋友圈海报,信息图设计,Canva高级,短视频封面,社交媒体视觉,品牌调性,内容排期",
        "is_available": True,
    },
    {
        "name": "谭明哲",
        "role": "品牌命名与文案策划",
        "description": "专做品牌命名和品牌文案。给 200+ 品牌起过名字、写过品牌故事和 Slogan。中文英文日文都能做，擅长用一句话说清一个品牌。",
        "skills": "品牌命名,文案创作,Slogan,品牌故事,多语言文案,创意策划,广告文案,品牌手册",
        "is_available": True,
    },
    {
        "name": "程雨萱",
        "role": "UI/UX 设计师",
        "description": "6 年互联网产品设计经验，前字节设计师。专做 SaaS 工具和 B 端产品的 UI/UX 设计。从交互原型到高保真视觉到设计规范，全套交付。",
        "skills": "Figma,UI设计,UX设计,交互原型,设计系统,用户测试,SaaS设计,B端设计",
        "is_available": True,
    },
    {
        "name": "魏俊杰",
        "role": "品牌空间与陈列设计",
        "description": "专做线下门店和展会的品牌空间设计。从门头到陈列到灯光，让品牌在线下也一眼被记住。做过餐饮、零售、展览空间。",
        "skills": "空间设计,门店设计,陈列设计,3D建模,效果图,材料选型,施工图,SketchUp",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 5. 想让财务对账自动完成 → 财务系统/自动化（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "张磊",
        "role": "财务系统开发工程师",
        "description": "10 年企业财务系统开发经验，精通金蝶用友等主流财务软件 API 对接。专做自动化对账、费用报销、财务报表自动化，帮企业省掉 80% 手工操作。",
        "skills": "Python,ERP,金蝶用友API,自动化脚本,Excel VBA,MySQL,财务流程,发票识别OCR",
        "is_available": True,
    },
    {
        "name": "邓丽华",
        "role": "财务自动化顾问",
        "description": "CPA + Python 双背景，既懂财务又懂技术。帮中小企业设计自动化对账流程、费用管控系统、自动生成财务报表。不用换财务软件，在现有系统上加自动化层。",
        "skills": "Python,财务流程,对账自动化,费控系统,财务报表,CPA,税务申报,数据分析",
        "is_available": True,
    },
    {
        "name": "霍伟强",
        "role": "金蝶用友二次开发",
        "description": "8 年 ERP 实施开发经验，精通金蝶云星空和用友 U8/T+ 的二次开发和接口定制。帮企业打通 ERP 和其他系统，消除数据孤岛。",
        "skills": "金蝶云星空,用友U8,ERP二次开发,API对接,SQL,插件开发,报表定制,财务模块",
        "is_available": True,
    },
    {
        "name": "傅晓婷",
        "role": "发票 OCR 与票据自动化",
        "description": "专做发票识别、票据自动化处理。做过每日 10000+ 张发票的自动识别和验真系统。对接税局接口，支持增值税发票、电子发票、行程单等。",
        "skills": "OCR识别,发票验真,税局API,票据处理,Python,图像处理,自动分类,数据录入",
        "is_available": True,
    },
    {
        "name": "纪鹏程",
        "role": "费用报销系统开发",
        "description": "帮企业开发定制费用报销和预算管控系统。从员工提单、审批流、发票上传到自动入账全流程。对接企业微信/钉钉，手机就能报销。",
        "skills": "费控系统,审批流,发票上传,预算管控,企业微信,钉钉集成,Python,Vue.js",
        "is_available": True,
    },
    {
        "name": "姜雪梅",
        "role": "税务筹划与申报自动化",
        "description": "注册税务师 + 技术背景。帮中小企业做税务合规的同时，用自动化工具搞定月度申报、发票管理、税务风险监控。",
        "skills": "税务筹划,纳税申报,发票管理,税务合规,Python自动化,税务风险,财税咨询,电子税务局",
        "is_available": True,
    },
    {
        "name": "肖永乐",
        "role": "银企直连与支付对接",
        "description": "5 年金融支付领域经验，精通多家银行银企直连接口。帮企业实现自动付款、自动收款、银行流水自动同步到财务系统。",
        "skills": "银企直连,支付网关,银行API,Python,资金管理,自动对账,SSL证书,报文协议",
        "is_available": True,
    },
    {
        "name": "尹慧芳",
        "role": "Excel 财务模板开发",
        "description": "专做中小企业能用得起的 Excel 财务自动化。把现金流量表、利润表、应收应付全部做成自动化模板，填数据就自动出报表。",
        "skills": "Excel VBA,财务报表,财务分析,自动化模板,应收应付,现金流管理,成本核算,利润分析",
        "is_available": True,
    },
    {
        "name": "罗志远",
        "role": "财务数据 BI 看板",
        "description": "帮财务团队做可视化看板，让 CFO 和老板一眼看懂公司财务状况。做过现金流预警看板、预算执行看板、应收账款看板。",
        "skills": "财务BI,现金流分析,预算管理,应收应付看板,Power BI,SQL,财务指标,Python",
        "is_available": True,
    },
    {
        "name": "韦思敏",
        "role": "多公司合并报表系统",
        "description": "帮集团型企业做多公司合并报表自动化。解决多主体、多币种、多准则的合并难题。用过 HFM、BPC，也能用 Python 轻量实现。",
        "skills": "合并报表,多币种,会计准则,Oracle HFM,SAP BPC,Python,SQL,抵消分录",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 6. 想在微信里把生意做起来 → 小程序/微信生态（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "何思远",
        "role": "小程序全栈开发",
        "description": "专注微信生态 4 年，交付 50+ 小程序项目。从商城、预约系统到工具类应用，做过餐饮、零售、家政等多行业。熟悉支付、会员、营销插件全套方案。",
        "skills": "微信小程序,UniApp,Vue.js,微信支付,云开发,SCRM,Node.js,MySQL",
        "is_available": True,
    },
    {
        "name": "唐明辉",
        "role": "微信商城与电商小程序",
        "description": "5 年电商小程序开发经验，做过 30+ 商城小程序。精通微信支付、分销体系、拼团秒杀等营销玩法。帮传统商家把生意搬到微信。",
        "skills": "电商小程序,微信支付,分销系统,拼团秒杀,会员体系,Vue.js,云开发,Node.js",
        "is_available": True,
    },
    {
        "name": "江紫嫣",
        "role": "小程序 UI 设计与交互",
        "description": "专做小程序 UI 设计，让界面符合微信设计规范又有品牌个性。做过电商、预约、社区团购等多种小程序类型的设计。",
        "skills": "小程序UI,微信设计规范,交互设计,Figma,用户研究,动效设计,组件库,用户体验",
        "is_available": True,
    },
    {
        "name": "邱博文",
        "role": "微信服务号开发",
        "description": "6 年微信公众号开发经验，做过菜单开发、模板消息、网页授权、JS-SDK 集成。帮企业用服务号做会员营销和客户服务。",
        "skills": "微信公众号,JS-SDK,模板消息,网页授权,菜单开发,PHP,Java,Spring Boot",
        "is_available": True,
    },
    {
        "name": "黎晓芸",
        "role": "企业微信开发与私域运营",
        "description": "专做企业微信生态开发：客户联系、客户群、客户朋友圈、离职继承等。帮企业搭建企微 SCRM 系统，打通小程序和视频号。",
        "skills": "企业微信API,SCRM,客户管理,会话存档,微信插件开发,PHP,Python,自动化流程",
        "is_available": True,
    },
    {
        "name": "钟佳豪",
        "role": "小程序云开发工程师",
        "description": "用微信云开发全套技术栈，一个人搞定小程序前后端。云函数+云数据库+云存储，不需要单独部署服务器。适合预算有限的初创项目。",
        "skills": "微信云开发,云函数,云数据库,云存储,小程序,TypeScript,NoSQL,快速原型",
        "is_available": True,
    },
    {
        "name": "龙雪晴",
        "role": "微信支付与会员系统",
        "description": "专做微信支付对接和会员卡系统。做过 50+ 商户的支付接入，打通小程序、公众号、线下扫码全场景支付。会员积分、储值、卡券全套。",
        "skills": "微信支付,会员系统,积分体系,储值卡,优惠券,支付对接,对账系统,卡券营销",
        "is_available": True,
    },
    {
        "name": "秦瑞林",
        "role": "微信小游戏开发",
        "description": "3 年微信小游戏开发经验，用 Cocos Creator 和 Laya 开发过多款休闲小游戏。做过答题、合成、跑酷等品类，懂买量和变现。",
        "skills": "Cocos Creator,LayaBox,微信小游戏,休闲游戏,游戏UI,广告变现,排行榜,社交分享",
        "is_available": True,
    },
    {
        "name": "夏小云",
        "role": "微信视频号运营与带货",
        "description": "帮品牌从 0 搭建视频号，从内容策划到直播带货到私域沉淀全流程。做过服装、食品、教育类视频号，单场直播 GMV 过 50 万。",
        "skills": "视频号运营,直播带货,内容策划,私域引流,选品策略,投流优化,数据分析,直播话术",
        "is_available": True,
    },
    {
        "name": "贺子豪",
        "role": "微信公众号代运营",
        "description": "帮中小企业代运营微信公众号，从内容策划、排版设计到粉丝增长。服务过 30+ 品牌，覆盖科技、生活、医疗等行业。",
        "skills": "公众号运营,内容策划,排版设计,粉丝增长,数据复盘,社群运营,热点营销,活动策划",
        "is_available": True,
    },

    # ═══════════════════════════════════════════════════════
    # 7. 想用短视频吸引精准客户 → 短视频/内容营销（10人）
    # ═══════════════════════════════════════════════════════
    {
        "name": "苏婉清",
        "role": "短视频内容策划",
        "description": "前 MCN 内容总监，现独立服务一人公司和中小企业。专注获客型短视频内容矩阵——从账号定位、脚本策划到投放优化，帮客户从 0 做到月均精准线索 200+。",
        "skills": "短视频脚本,剪映,内容策略,账号运营,私域引流,数据分析,投放优化,口播文案",
        "is_available": True,
    },
    {
        "name": "袁志豪",
        "role": "抖音信息流投手",
        "description": "4 年抖音投放经验，月消耗 200 万+。精通巨量引擎和千川，擅长从 0 搭建投放账户。做过教育、电商、本地生活等行业的获客投放。",
        "skills": "巨量引擎,千川投放,信息流广告,素材优化,ROI优化,人群定向,落地页优化,数据分析",
        "is_available": True,
    },
    {
        "name": "吕诗曼",
        "role": "短视频拍摄与剪辑",
        "description": "一个人扛起拍摄+灯光+剪辑全套。做过探店、口播、产品展示、剧情等多种类型短视频。给 20+ 企业号提供过长期视频供应服务。",
        "skills": "视频拍摄,剪映专业版,达芬奇调色,布光,口播拍摄,产品拍摄,探店拍摄,后期剪辑",
        "is_available": True,
    },
    {
        "name": "熊凯文",
        "role": "直播带货运营",
        "description": "帮品牌从 0 搭建抖音直播间，从人货场到话术到投流全流程。做过服装、美妆、食品直播间，单场 GMV 最高 100 万。",
        "skills": "直播运营,抖音直播,千川投放,话术设计,场控,选品排品,数据复盘,主播培训",
        "is_available": True,
    },
    {
        "name": "梅晓冉",
        "role": "IP 口播账号全案策划",
        "description": "专做创始人/专家个人 IP 口播账号。从选题策略、逐字稿撰写到拍摄指导到运营复盘。帮 30+ 老板用口播获取精准客户。",
        "skills": "IP打造,口播脚本,选题策划,人设设计,拍摄指导,账号运营,变现路径,私域转化",
        "is_available": True,
    },
    {
        "name": "宋建峰",
        "role": "短视频 SEO 与搜索获客",
        "description": "帮你做的短视频不仅能刷到、还能被搜到。精通抖音搜索排名优化，让精准客户搜关键词就能找到你的视频。低预算也能稳定获客。",
        "skills": "抖音SEO,关键词布局,搜索优化,标题优化,标签策略,短视频矩阵,批量发布,数据分析",
        "is_available": True,
    },
    {
        "name": "童雨欣",
        "role": "小红书运营与种草营销",
        "description": "3 年小红书运营经验，帮品牌做种草笔记、达人合作、信息流投放。从 0 做到月均品牌搜索量 10 万+，帮多个消费品牌在小红书冷启动。",
        "skills": "小红书运营,种草笔记,达人合作,信息流,品牌号,内容策划,SEO优化,蒲公英平台",
        "is_available": True,
    },
    {
        "name": "贾明宇",
        "role": "B 站视频策划与制作",
        "description": "专做 B 站中长视频内容，帮科技、知识类品牌做深度内容营销。从选题研究到脚本到后期剪辑全流程，做出过多个百万播放视频。",
        "skills": "B站运营,中长视频,脚本撰写,后期剪辑,选题研究,知识营销,PR剪辑,AE特效",
        "is_available": True,
    },
    {
        "name": "尤思涵",
        "role": "短视频数据与增长分析",
        "description": "用数据驱动短视频增长。帮客户分析完播率、互动率、粉丝画像，找到爆款规律和优化方向。不做内容制作，只做数据诊断和策略建议。",
        "skills": "数据分析,短视频数据,粉丝画像,完播率分析,AB测试,内容策略,巨量云图,竞品分析",
        "is_available": True,
    },
    {
        "name": "石志鹏",
        "role": "短视频矩阵批量运营",
        "description": "帮企业低成本搭建短视频矩阵，一人管理 10+ 账号，批量生产内容。用工具+模板实现日产 50 条短视频，铺量获客。适合有标准化产品的中小企业。",
        "skills": "矩阵运营,批量剪辑,AI配音,自动化发布,模板设计,多账号管理,获客策略,工具搭建",
        "is_available": True,
    },
]


def main():
    client = get_supabase()
    success = 0
    failed = 0

    for p in PROFILES:
        try:
            resp = client.table("opc_profiles").insert(p).execute()
            inserted = resp.data[0] if resp.data else None
            print(f"✓ {p['name']} ({p['role']})")
            success += 1
        except Exception as e:
            print(f"✗ {p['name']} 插入失败: {e}")
            failed += 1

    print(f"\n完成：成功 {success}，失败 {failed}，共 {len(PROFILES)} 条。")


if __name__ == "__main__":
    main()
