# -*- coding: utf-8 -*-
"""UniPulse 就业数据 - 前100所大学的热门专业就业信息
薪资单位: 中国高校用人民币(年), 海外高校用美元(年)
数据来源: 各大学就业质量报告、QS Graduate Employability、公开统计数据
"""
UNI_PROGRAMS = [
    # ── 美国 TOP ──
    {"uni_id":1,"program_name":"计算机科学","salary_avg":135000,"salary_entry":95000,"employment_rate":96,"pressure":6,"prospects":9,"description":"哈佛CS毕业生深受科技巨头和金融量化领域青睐，平均起薪全美前列"},
    {"uni_id":1,"program_name":"经济学","salary_avg":110000,"salary_entry":72000,"employment_rate":92,"pressure":5,"prospects":8,"description":"哈佛经济学是华尔街投行和咨询公司的核心生源，就业网络极强"},
    {"uni_id":1,"program_name":"法学","salary_avg":160000,"salary_entry":125000,"employment_rate":89,"pressure":8,"prospects":7,"description":"哈佛法学院毕业生起薪全美最高之一，大型律所首选"},
    {"uni_id":1,"program_name":"医学","salary_avg":220000,"salary_entry":150000,"employment_rate":95,"pressure":9,"prospects":8,"description":"哈佛医学院毕业生住院医师匹配率接近100%，全美顶尖"},
    {"uni_id":2,"program_name":"计算机科学","salary_avg":140000,"salary_entry":100000,"employment_rate":97,"pressure":5,"prospects":10,"description":"MIT CS是AI和系统研究的全球领导者，硅谷和学术界双重优势"},
    {"uni_id":2,"program_name":"电子工程","salary_avg":125000,"salary_entry":88000,"employment_rate":95,"pressure":6,"prospects":9,"description":"MIT EECS毕业生在半导体、机器人、自动驾驶领域极具竞争力"},
    {"uni_id":2,"program_name":"数学","salary_avg":115000,"salary_entry":78000,"employment_rate":93,"pressure":5,"prospects":8,"description":"MIT数学毕业生在量化金融和AI算法领域有独特优势"},
    {"uni_id":2,"program_name":"机械工程","salary_avg":105000,"salary_entry":75000,"employment_rate":94,"pressure":6,"prospects":8,"description":"MIT机械工程在制造业和航空航天领域就业优势明显"},
    {"uni_id":3,"program_name":"计算机科学","salary_avg":130000,"salary_entry":92000,"employment_rate":96,"pressure":6,"prospects":9,"description":"斯坦福CS地处硅谷核心，创业和科技公司就业双重通道"},
    {"uni_id":3,"program_name":"商科/MBA","salary_avg":155000,"salary_entry":110000,"employment_rate":94,"pressure":5,"prospects":9,"description":"斯坦福GSB毕业生平均薪资全美商学院前三，VC/PE首选"},
    {"uni_id":3,"program_name":"电子工程","salary_avg":120000,"salary_entry":85000,"employment_rate":95,"pressure":6,"prospects":9,"description":"斯坦福EE在芯片设计和AI硬件领域与硅谷深度绑定"},
    {"uni_id":3,"program_name":"产品设计","salary_avg":105000,"salary_entry":72000,"employment_rate":91,"pressure":5,"prospects":8,"description":"斯坦福d.school设计思维方法论深受科技公司追捧"},
    {"uni_id":4,"program_name":"物理","salary_avg":95000,"salary_entry":65000,"employment_rate":88,"pressure":6,"prospects":7,"description":"Caltech物理毕业生在学术研究和高科技领域均有建树"},
    {"uni_id":4,"program_name":"计算机科学","salary_avg":128000,"salary_entry":90000,"employment_rate":95,"pressure":5,"prospects":9,"description":"Caltech CS小而精，在量子计算和理论CS领域独树一帜"},
    {"uni_id":4,"program_name":"航空航天工程","salary_avg":110000,"salary_entry":78000,"employment_rate":93,"pressure":6,"prospects":8,"description":"Caltech/JPL深度合作，航天领域就业直通车"},
    {"uni_id":5,"program_name":"经济学","salary_avg":105000,"salary_entry":70000,"employment_rate":91,"pressure":5,"prospects":8,"description":"芝加哥经济学派发源地，学术和金融界双重影响力"},
    {"uni_id":5,"program_name":"金融","salary_avg":130000,"salary_entry":85000,"employment_rate":90,"pressure":7,"prospects":8,"description":"芝加哥金融项目与CME等交易所紧密合作，量化方向突出"},
    {"uni_id":5,"program_name":"数学","salary_avg":100000,"salary_entry":68000,"employment_rate":89,"pressure":5,"prospects":8,"description":"芝加哥数学强调分析训练，量化金融和学术研究双通道"},
    {"uni_id":6,"program_name":"商科/MBA","salary_avg":150000,"salary_entry":105000,"employment_rate":93,"pressure":5,"prospects":9,"description":"沃顿商学院全球顶级，投行、咨询、PE三大通道全开"},
    {"uni_id":6,"program_name":"计算机科学","salary_avg":125000,"salary_entry":88000,"employment_rate":94,"pressure":6,"prospects":9,"description":"宾大CS与沃顿交叉优势，金融科技领域就业突出"},
    {"uni_id":6,"program_name":"法学","salary_avg":155000,"salary_entry":120000,"employment_rate":88,"pressure":8,"prospects":7,"description":"宾大法学院毕业生在大型律所就业率全美前列"},
    {"uni_id":7,"program_name":"金融工程","salary_avg":140000,"salary_entry":95000,"employment_rate":92,"pressure":7,"prospects":8,"description":"哥大金工项目地处纽约金融中心，华尔街直通车"},
    {"uni_id":7,"program_name":"计算机科学","salary_avg":128000,"salary_entry":90000,"employment_rate":95,"pressure":6,"prospects":9,"description":"哥大CS在NLP和机器学习方向强大，纽约科技行业首选"},
    {"uni_id":7,"program_name":"法学","salary_avg":158000,"salary_entry":122000,"employment_rate":87,"pressure":8,"prospects":7,"description":"哥大法学院是纽约大型律所的核心生源"},
    {"uni_id":8,"program_name":"法学","salary_avg":155000,"salary_entry":118000,"employment_rate":88,"pressure":8,"prospects":7,"description":"耶鲁法学院全美排名常年第1，学术和实务双强"},
    {"uni_id":8,"program_name":"经济学","salary_avg":105000,"salary_entry":70000,"employment_rate":90,"pressure":5,"prospects":8,"description":"耶鲁经济学在学术和政策领域影响力巨大"},
    {"uni_id":8,"program_name":"医学","salary_avg":210000,"salary_entry":145000,"employment_rate":94,"pressure":9,"prospects":8,"description":"耶鲁医学院在临床和科研领域均处于顶尖水平"},
    {"uni_id":9,"program_name":"计算机科学","salary_avg":118000,"salary_entry":82000,"employment_rate":93,"pressure":6,"prospects":9,"description":"普林斯顿CS理论方向全美顶尖，学术和工业界双通道"},
    {"uni_id":9,"program_name":"数学","salary_avg":98000,"salary_entry":65000,"employment_rate":88,"pressure":5,"prospects":8,"description":"普林斯顿数学全球最强之一，菲尔兹奖得主摇篮"},
    {"uni_id":9,"program_name":"物理","salary_avg":92000,"salary_entry":62000,"employment_rate":87,"pressure":6,"prospects":7,"description":"普林斯顿物理在理论和实验物理领域均为全球标杆"},
    {"uni_id":10,"program_name":"计算机科学","salary_avg":122000,"salary_entry":85000,"employment_rate":94,"pressure":6,"prospects":9,"description":"布朗CS以开放课程体系著称，跨学科能力强"},
    {"uni_id":10,"program_name":"医学","salary_avg":195000,"salary_entry":135000,"employment_rate":93,"pressure":9,"prospects":8,"description":"布朗医学院PLME项目为全美少数直接医学项目之一"},
    {"uni_id":12,"program_name":"计算机科学","salary_avg":120000,"salary_entry":84000,"employment_rate":94,"pressure":6,"prospects":9,"description":"康奈尔CS在系统、数据库和NLP方向突出"},
    {"uni_id":12,"program_name":"建筑学","salary_avg":78000,"salary_entry":55000,"employment_rate":85,"pressure":7,"prospects":7,"description":"康奈尔建筑学院全美第1，就业网络遍布全球顶级事务所"},
    {"uni_id":12,"program_name":"酒店管理","salary_avg":72000,"salary_entry":48000,"employment_rate":92,"pressure":4,"prospects":7,"description":"康奈尔酒店学院全球最强，高端酒店集团首选"},
    {"uni_id":13,"program_name":"计算机科学","salary_avg":125000,"salary_entry":88000,"employment_rate":95,"pressure":6,"prospects":9,"description":"UCB CS是硅谷科技人才最大供应源，就业率极高"},
    {"uni_id":13,"program_name":"电子工程","salary_avg":115000,"salary_entry":80000,"employment_rate":94,"pressure":6,"prospects":9,"description":"UCB EECS在芯片和AI硬件方向与硅谷紧密联动"},
    {"uni_id":13,"program_name":"商科","salary_avg":110000,"salary_entry":72000,"employment_rate":91,"pressure":6,"prospects":8,"description":"Haas商学院本科项目竞争激烈，就业质量极高"},
    {"uni_id":14,"program_name":"计算机科学","salary_avg":120000,"salary_entry":84000,"employment_rate":94,"pressure":6,"prospects":9,"description":"UCLA CS在AI和生物信息学方向表现突出"},
    {"uni_id":14,"program_name":"医学","salary_avg":200000,"salary_entry":138000,"employment_rate":94,"pressure":9,"prospects":8,"description":"UCLA医学院在临床医学和生物医学研究领域领先"},
    {"uni_id":14,"program_name":"影视传媒","salary_avg":85000,"salary_entry":52000,"employment_rate":82,"pressure":8,"prospects":7,"description":"地处好莱坞，影视行业就业天然优势"},
    {"uni_id":15,"program_name":"工程","salary_avg":108000,"salary_entry":76000,"employment_rate":93,"pressure":6,"prospects":8,"description":"密歇根工程学院全美前5，汽车和制造业就业优势明显"},
    {"uni_id":15,"program_name":"商科","salary_avg":108000,"salary_entry":72000,"employment_rate":91,"pressure":5,"prospects":8,"description":"Ross商学院在供应链和运营管理方向全美顶级"},
    {"uni_id":15,"program_name":"计算机科学","salary_avg":115000,"salary_entry":80000,"employment_rate":93,"pressure":6,"prospects":9,"description":"密歇根CS在系统、HCI和机器人方向有较强实力"},
    {"uni_id":19,"program_name":"计算机科学","salary_avg":118000,"salary_entry":82000,"employment_rate":93,"pressure":6,"prospects":9,"description":"UCSD CS在生物信息和系统方向突出"},
    {"uni_id":19,"program_name":"生物科学","salary_avg":82000,"salary_entry":55000,"employment_rate":86,"pressure":7,"prospects":7,"description":"UCSD生物科学在基因组学和生物医药方向实力强"},
    {"uni_id":26,"program_name":"计算机科学","salary_avg":118000,"salary_entry":82000,"employment_rate":93,"pressure":6,"prospects":9,"description":"UW CS在西雅图科技行业就业优势巨大（微软、亚马逊）"},
    {"uni_id":26,"program_name":"医学","salary_avg":195000,"salary_entry":135000,"employment_rate":93,"pressure":9,"prospects":8,"description":"UW医学院在初级保健和农村医疗方向全美领先"},
    {"uni_id":33,"program_name":"工程","salary_avg":100000,"salary_entry":70000,"employment_rate":92,"pressure":6,"prospects":8,"description":"普渡工程全美顶级，航空航天方向尤其突出"},
    {"uni_id":33,"program_name":"计算机科学","salary_avg":110000,"salary_entry":78000,"employment_rate":93,"pressure":6,"prospects":9,"description":"普渡CS在系统和安全方向有传统优势"},
    {"uni_id":101,"program_name":"计算机科学","salary_avg":125000,"salary_entry":88000,"employment_rate":94,"pressure":6,"prospects":9,"description":"杜克CS在AI和生物计算方向增长迅速"},
    {"uni_id":101,"program_name":"医学","salary_avg":205000,"salary_entry":142000,"employment_rate":94,"pressure":9,"prospects":8,"description":"杜克医学院全美顶级，临床和科研双强"},

    # ── 英国 TOP ──
    {"uni_id":157,"program_name":"计算机科学","salary_avg":65000,"salary_entry":45000,"employment_rate":93,"pressure":5,"prospects":9,"description":"牛津CS理论方向全球顶尖，学术和工业界双优"},
    {"uni_id":157,"program_name":"法学","salary_avg":75000,"salary_entry":52000,"employment_rate":88,"pressure":7,"prospects":8,"description":"牛津法学院在英国Magic Circle律所就业率最高"},
    {"uni_id":157,"program_name":"经济学","salary_avg":72000,"salary_entry":48000,"employment_rate":90,"pressure":5,"prospects":8,"description":"牛津PPE项目是英国政商界精英摇篮"},
    {"uni_id":158,"program_name":"工程","salary_avg":60000,"salary_entry":42000,"employment_rate":92,"pressure":6,"prospects":8,"description":"剑桥工程在英国制造业和科技行业认可度极高"},
    {"uni_id":158,"program_name":"计算机科学","salary_avg":68000,"salary_entry":46000,"employment_rate":94,"pressure":5,"prospects":9,"description":"剑桥CS在AI和图形学方向全球领先"},
    {"uni_id":158,"program_name":"医学","salary_avg":82000,"salary_entry":55000,"employment_rate":95,"pressure":8,"prospects":8,"description":"剑桥医学院在英国NHS体系中就业保障极强"},
    {"uni_id":159,"program_name":"计算机科学","salary_avg":62000,"salary_entry":43000,"employment_rate":92,"pressure":6,"prospects":9,"description":"帝国理工CS毕业生在伦敦金融城和科技行业就业率极高"},
    {"uni_id":159,"program_name":"工程","salary_avg":58000,"salary_entry":40000,"employment_rate":93,"pressure":6,"prospects":8,"description":"帝国理工工程是英国最顶尖的工程项目之一"},
    {"uni_id":159,"program_name":"医学","salary_avg":80000,"salary_entry":53000,"employment_rate":95,"pressure":8,"prospects":8,"description":"帝国理工医学院在临床科研和公共卫生领域全球知名"},
    {"uni_id":160,"program_name":"建筑学","salary_avg":48000,"salary_entry":32000,"employment_rate":84,"pressure":7,"prospects":7,"description":"UCL Bartlett建筑学院全球第1，顶级事务所核心生源"},
    {"uni_id":160,"program_name":"计算机科学","salary_avg":58000,"salary_entry":40000,"employment_rate":91,"pressure":6,"prospects":8,"description":"UCL CS在AI安全、机器学习方向实力雄厚"},
    {"uni_id":162,"program_name":"经济学","salary_avg":72000,"salary_entry":50000,"employment_rate":89,"pressure":5,"prospects":8,"description":"LSE经济学全球顶级，金融和政策领域影响力巨大"},
    {"uni_id":162,"program_name":"金融","salary_avg":78000,"salary_entry":54000,"employment_rate":90,"pressure":6,"prospects":8,"description":"LSE金融是伦敦金融城的核心人才来源"},
    {"uni_id":162,"program_name":"法学","salary_avg":70000,"salary_entry":48000,"employment_rate":87,"pressure":7,"prospects":7,"description":"LSE法学院在国际法和人权法方向独具特色"},

    # ── 中国 TOP ──
    {"uni_id":333,"program_name":"计算机科学","salary_avg":320000,"salary_entry":220000,"employment_rate":98,"pressure":7,"prospects":9,"description":"清华CS是中国科技行业的黄埔军校，BAT和AI公司首选"},
    {"uni_id":333,"program_name":"电子工程","salary_avg":280000,"salary_entry":200000,"employment_rate":97,"pressure":7,"prospects":9,"description":"清华EE在芯片和通信领域就业优势压倒性"},
    {"uni_id":333,"program_name":"建筑学","salary_avg":220000,"salary_entry":150000,"employment_rate":92,"pressure":7,"prospects":7,"description":"清华建筑学院中国最强，顶级设计院直通车"},
    {"uni_id":334,"program_name":"计算机科学","salary_avg":300000,"salary_entry":210000,"employment_rate":97,"pressure":7,"prospects":9,"description":"北大CS在AI和自然语言处理方向国内领先"},
    {"uni_id":334,"program_name":"法学","salary_avg":200000,"salary_entry":130000,"employment_rate":90,"pressure":7,"prospects":7,"description":"北大法学院中国最顶尖，红圈所核心生源"},
    {"uni_id":334,"program_name":"经济学","salary_avg":250000,"salary_entry":160000,"employment_rate":92,"pressure":6,"prospects":8,"description":"北大经济学院和光华管理学院双重优势"},
    {"uni_id":335,"program_name":"金融","salary_avg":280000,"salary_entry":180000,"employment_rate":93,"pressure":7,"prospects":8,"description":"复旦金融是上海金融圈的核心人才来源"},
    {"uni_id":335,"program_name":"医学","salary_avg":180000,"salary_entry":120000,"employment_rate":95,"pressure":8,"prospects":8,"description":"复旦医学院（原上医）在长三角医疗体系影响力巨大"},
    {"uni_id":335,"program_name":"新闻传播","salary_avg":150000,"salary_entry":100000,"employment_rate":88,"pressure":7,"prospects":6,"description":"复旦新闻学院中国最强，主流媒体和互联网内容方向"},
    {"uni_id":336,"program_name":"计算机科学","salary_avg":290000,"salary_entry":200000,"employment_rate":96,"pressure":7,"prospects":9,"description":"浙大CS在计算机视觉和图形学方向国际知名"},
    {"uni_id":336,"program_name":"电子工程","salary_avg":260000,"salary_entry":180000,"employment_rate":95,"pressure":7,"prospects":8,"description":"浙大EE在电力电子和光电方向国内领先"},
    {"uni_id":337,"program_name":"计算机科学","salary_avg":280000,"salary_entry":190000,"employment_rate":95,"pressure":7,"prospects":9,"description":"上交CS在网络安全和AI方向实力雄厚"},
    {"uni_id":337,"program_name":"机械工程","salary_avg":200000,"salary_entry":140000,"employment_rate":93,"pressure":6,"prospects":7,"description":"上交机械工程在汽车和高端制造方向国内领先"},
    {"uni_id":337,"program_name":"医学","salary_avg":170000,"salary_entry":115000,"employment_rate":94,"pressure":8,"prospects":8,"description":"上交医学院（原上二医）临床医学实力极强"},

    # ── 加拿大 ──
    {"uni_id":135,"program_name":"计算机科学","salary_avg":85000,"salary_entry":60000,"employment_rate":93,"pressure":5,"prospects":9,"description":"多大CS是加拿大科技行业最大人才来源，AI方向全球知名"},
    {"uni_id":135,"program_name":"商科","salary_avg":78000,"salary_entry":52000,"employment_rate":90,"pressure":5,"prospects":8,"description":"Rotman商学院是加拿大金融中心核心生源"},
    {"uni_id":135,"program_name":"医学","salary_avg":180000,"salary_entry":120000,"employment_rate":94,"pressure":8,"prospects":8,"description":"多大医学院是加拿大最大医学人才培养基地"},
    {"uni_id":136,"program_name":"医学","salary_avg":175000,"salary_entry":115000,"employment_rate":93,"pressure":8,"prospects":8,"description":"麦吉尔医学院在加拿大医疗体系中声誉卓著"},
    {"uni_id":136,"program_name":"法学","salary_avg":82000,"salary_entry":55000,"employment_rate":87,"pressure":6,"prospects":7,"description":"麦吉尔法学院是加拿大双语法律教育的标杆"},

    # ── 瑞士 ──
    {"uni_id":236,"program_name":"计算机科学","salary_avg":110000,"salary_entry":78000,"employment_rate":95,"pressure":4,"prospects":9,"description":"ETH Zurich CS是欧洲科技行业的核心人才来源"},
    {"uni_id":236,"program_name":"工程","salary_avg":105000,"salary_entry":72000,"employment_rate":94,"pressure":5,"prospects":8,"description":"ETH工程在精密制造和机器人方向全球领先"},
    {"uni_id":236,"program_name":"建筑学","salary_avg":75000,"salary_entry":52000,"employment_rate":86,"pressure":6,"prospects":7,"description":"ETH建筑学院在欧洲建筑界影响力极大"},

    # ── 新加坡 ──
    {"uni_id":413,"program_name":"计算机科学","salary_avg":72000,"salary_entry":50000,"employment_rate":95,"pressure":5,"prospects":9,"description":"NUS CS在亚太科技行业就业优势明显，新加坡科技枢纽"},
    {"uni_id":413,"program_name":"商科","salary_avg":68000,"salary_entry":46000,"employment_rate":92,"pressure":5,"prospects":8,"description":"NUS商学院是亚太金融和咨询行业的核心生源"},
    {"uni_id":414,"program_name":"计算机科学","salary_avg":70000,"salary_entry":48000,"employment_rate":94,"pressure":5,"prospects":9,"description":"NTU CS在AI和机器人方向增长迅速"},

    # ── 澳大利亚 ──
    {"uni_id":475,"program_name":"医学","salary_avg":150000,"salary_entry":100000,"employment_rate":96,"pressure":7,"prospects":8,"description":"墨大医学院在澳洲医疗体系认可度最高"},
    {"uni_id":475,"program_name":"商科","salary_avg":70000,"salary_entry":48000,"employment_rate":89,"pressure":5,"prospects":7,"description":"墨大商学院是亚太金融和咨询行业的重要生源"},
    {"uni_id":477,"program_name":"法学","salary_avg":80000,"salary_entry":55000,"employment_rate":87,"pressure":6,"prospects":7,"description":"悉尼法学院在澳洲法律行业地位顶尖"},

    # ── 日本 ──
    {"uni_id":417,"program_name":"工程","salary_avg":6500000,"salary_entry":4500000,"employment_rate":95,"pressure":6,"prospects":7,"description":"东大工学部是日本制造业和科技行业最高殿堂"},
    {"uni_id":417,"program_name":"医学","salary_avg":12000000,"salary_entry":8000000,"employment_rate":97,"pressure":8,"prospects":8,"description":"东大医学部在日本医疗界地位不可动摇"},
    {"uni_id":418,"program_name":"工程","salary_avg":5800000,"salary_entry":4000000,"employment_rate":94,"pressure":6,"prospects":7,"description":"京大工学部在基础研究和材料科学方向突出"},

    # ── 韩国 ──
    {"uni_id":430,"program_name":"商科","salary_avg":55000000,"salary_entry":38000000,"employment_rate":91,"pressure":7,"prospects":7,"description":"首尔大商科是韩国财阀企业核心生源"},
    {"uni_id":430,"program_name":"医学","salary_avg":90000000,"salary_entry":60000000,"employment_rate":96,"pressure":8,"prospects":8,"description":"首尔大医学部在韩国医疗界地位最高"},

    # ── 德国 ──
    {"uni_id":197,"program_name":"工程","salary_avg":60000,"salary_entry":45000,"employment_rate":94,"pressure":4,"prospects":8,"description":"TUM工程在德国制造业和汽车行业认可度最高"},
    {"uni_id":197,"program_name":"计算机科学","salary_avg":62000,"salary_entry":44000,"employment_rate":93,"pressure":5,"prospects":8,"description":"TUM CS在欧洲科技行业就业前景优秀"},

    # ── 法国 ──
    {"uni_id":220,"program_name":"工程","salary_avg":55000,"salary_entry":40000,"employment_rate":92,"pressure":5,"prospects":8,"description":"巴黎综合理工是法国工程师精英教育的最高殿堂"},
    {"uni_id":222,"program_name":"商科","salary_avg":70000,"salary_entry":50000,"employment_rate":90,"pressure":6,"prospects":8,"description":"巴黎高商HEC是欧洲商界精英摇篮，投行咨询首选"},

    # ── 荷兰 ──
    {"uni_id":242,"program_name":"工程","salary_avg":52000,"salary_entry":38000,"employment_rate":91,"pressure":4,"prospects":8,"description":"代尔夫特理工工程在欧洲技术行业就业前景优秀"},
    {"uni_id":242,"program_name":"建筑学","salary_avg":45000,"salary_entry":32000,"employment_rate":85,"pressure":6,"prospects":7,"description":"代尔夫特建筑学院全球顶级，可持续设计方向领先"},

    # ── 香港 ──
    {"uni_id":395,"program_name":"金融","salary_avg":450000,"salary_entry":300000,"employment_rate":92,"pressure":7,"prospects":8,"description":"港大金融是香港金融圈核心生源，投行和资管首选"},
    {"uni_id":395,"program_name":"医学","salary_avg":900000,"salary_entry":600000,"employment_rate":95,"pressure":8,"prospects":8,"description":"港大医学院是香港医疗体系最重要的培养基地"},
    {"uni_id":396,"program_name":"商科","salary_avg":380000,"salary_entry":250000,"employment_rate":90,"pressure":6,"prospects":8,"description":"港中文商学院在亚太金融和市场营销方向实力强"},
    {"uni_id":397,"program_name":"计算机科学","salary_avg":360000,"salary_entry":240000,"employment_rate":93,"pressure":6,"prospects":9,"description":"港科大CS在数据科学和AI方向亚太领先"},

    # ── 更多美国大学 ──
    {"uni_id":34,"program_name":"计算机科学","salary_avg":120000,"salary_entry":84000,"employment_rate":93,"pressure":6,"prospects":9,"description":"UCB分校CS就业同样强劲，硅谷科技行业直通车"},
    {"uni_id":6,"program_name":"护理学","salary_avg":85000,"salary_entry":62000,"employment_rate":96,"pressure":6,"prospects":8,"description":"宾大护理学院全美顶级，就业率极高"},
]
