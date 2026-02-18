SKILL_ORDER = ["Languages", "Frameworks", "Databases", 
               "Infrastructure", "Tools", "Methodologies", 
               "Security", "Data Engineering", "Industrial_IT", 
               "Business_Analytics", "Engineering_Software", "AI_ML"]
SKILL_MAP = {

    "Languages": [
        "python", "java", "javascript", "typescript", "golang", "go",
        "c++", "c#", "f#", "objective-c",
        "php", "ruby", "kotlin", "swift",
        "scala", "groovy",
        "rust", "dart", "elixir", "haskell", "erlang",
        "bash", "shell", "powershell",
        "matlab", "r", "sas",
        "solidity", "vyper",
        "assembly", "vba", "cobol", "fortran", "js", "ts", "html", "css", "1c", "1с"
    ],

    "Frameworks": [
        # Python
        "django", "flask", "fastapi", "aiohttp", "tornado",
        "celery", "pydantic", "sqlalchemy", "asyncio",

        # Java
        "spring", "spring boot", "spring mvc",
        "hibernate", "jpa", "quarkus", "micronaut",

        # JS / Frontend
        "react", "react.js", "next.js",
        "vue", "vue.js", "nuxt",
        "angular", "angularjs",
        "svelte", "redux", "mobx",
        "zustand", "rxjs", "node.js", "nodejs", "node",
        "express", "nest.js", "koa", "jquery"

        # Node
        "node.js", "nodejs", "express", "nest.js", "koa",

        # PHP
        "laravel", "symfony", "yii", "codeigniter",

        # .NET
        ".net", ".net core", "asp.net", "entity framework",

        # Mobile
        "flutter", "react native", "android sdk", "ios sdk",
        "jetpack compose", "swiftui",

        # Data / ML
        "tensorflow", "pytorch", "keras",
        "scikit-learn","scikit", "xgboost", "lightgbm",
        "pandas", "numpy", "opencv",
        "huggingface", "transformers",

        # Other
        "graphql", "apollo", "grpc",
        "bootstrap", "tailwind", "material ui",
        
        # R
        "shiny", "ggplot2", "dplyr", "Telegrambot",
        #1c
        "bitrix", "bitrix24", "1c enterprise", "1с предприятие"
    ],

    "Infrastructure": [
        "docker", "docker-compose",
        "kubernetes", "k8s", "helm",
        "ansible", "terraform", "pulumi",
        "jenkins", "gitlab ci", "gitlab ci/cd", "ci/cd", "github actions",
        "teamcity", "circleci",
        "aws", "amazon web services",
        "gcp", "google cloud",
        "azure", "microsoft azure",
        "digitalocean",
        "nginx", "apache", "traefik",
        "prometheus", "grafana",
        "vault", "consul",
        "istio", "linkerd",
        "cloudflare",
        "linux", "ubuntu", "debian", "centos", "http", 
        "https", "dns", "tcp/ip", "nginx", "websocket", "postfix"
    ],

    "Databases": [
        "sql", 
        "postgresql", "postgres",
        "mysql", "mariadb",
        "mongodb",
        "redis",
        "clickhouse",
        "elasticsearch",
        "oracle",
        "cassandra",
        "sqlite",
        "dynamodb",
        "neo4j",
        "timescaledb",
        "cockroachdb",
        "snowflake",
        "bigquery",
        "hadoop",
        "hive",
        "presto",
        "redshift",
        "influxdb"
    ],

    "Tools": [
        "pyright", "webdriver", "excel", "git", "github", "gitlab", "bitbucket",
        "jira", "confluence",
        "postman", "insomnia",
        "swagger", "openapi",
        "selenium", "playwright", "cypress",
        "pytest", "unittest", "jest", "mocha",
        "allure", "sonarqube",
        "kafka", "rabbitmq", "nats",
        "airflow", "luigi",
        "tableau", "power bi", "superset", "FineBI",
        "figma", "webpack", "vite", "babel",
        "gradle", "maven",
        "npm", "yarn", "pnpm",
        "linux", "bash", "zsh",
        "jira", "notion"
    ],
    "Data Engineering": [
        "ETL",
    ],
    
    "Methodologies": [
        "agile", "scrum", "kanban",
        "tdd", "bdd",
        "ddd", "clean architecture",
        "microservices", "monolith",
        "event-driven", "cqrs",
        "rest", "rest api",
        "soap",
        "ci/cd", "devops",
        "oop", "solid"
    ],

    "Security": [
        "oauth", "oauth2", "jwt",
        "soap", "grpc"
        "saml", "openid",
        "xss", "csrf", "owasp",
        "penetration testing",
        "burp suite",
        "wireshark",
        "ssl", "tls",
        "agile", "scrum"
    ],
    
    "Industrial_IT": [
    "асутп", "scada", "plc", "плк", "modbus", "opc ua", 
    "промышленная автоматизация", "hmi", "mes"
    ],
    
    "Business_Analytics": [
    "ctr", "roi", "romi", "cpl", "cac", "ltv", 
    "conversion", "конверсия", "unit economics", "юнит-экономика",
    "churn rate", "retention"
    ],
    
    "Engineering_Software": [
        "solidworks", "fusion 360", "компас-3d", "autocad", 
        "matlab", "simulink", "gazebo", "ansys"
    ],
    "AI_ML": [
    "asr", "tts", "nlu", "nlp", "llm", 
    "stt", "speech-to-text", "text-to-speech",
    "voice assistant", "голосовой ассистент"
    ]   
}


CATEGORIES = {

    "AI, ML & LLM": [
        "ai", "artificial intelligence", "искусственный интеллект",
        "ml", "machine learning", "машинное обучение",
        "deep learning", "dl",
        "llm", "large language model",
        "nlp", "natural language processing",
        "computer vision", "cv", "vision",
        "нейросеть", "нейронная сеть",
        "transformer", "bert", "gpt", "rag",
        "prompt", "prompt engineering", "промпт",
        "генеративный", "generative ai",
        "fine-tuning", "обучение модели",
        "data labeling", "разметка данных",
        "ml engineer", "ai engineer",
        "mlops", "model deployment",
        "reinforcement learning",
        "rpa", "robotic process automation"
    ],

    "QA & Automation": [
        "qa", "quality assurance",
        "тестировщик", "инженер по тестированию",
        "test engineer", "automation engineer",
        "manual qa", "manual testing",
        "автотест", "автоматизация тестирования",
        "тестирование", "functional testing",
        "regression testing", "smoke test",
        "нагрузочный", "load testing",
        "performance testing",
        "selenium", "cypress", "playwright",
        "pytest", "junit", "testng",
        "bdd", "tdd",
        "api testing", "postman",
        "qa lead", "test lead"
    ],

    "Cybersecurity": [
        "cybersecurity", "information security",
        "иб", "информационная безопасность",
        "pentest", "penetration testing", "пентестер",
        "ethical hacking", "red team", "blue team",
        "appsec", "application security",
        "soc", "siem",
        "reverse engineering", "реверс",
        "malware analysis",
        "threat hunting",
        "incident response",
        "cryptography", "шифрование",
        "firewall", "ids", "ips",
        "devsecops",
        "owasp", "vulnerability",
        "security analyst"
    ],

    "Electronics & Hardware": [
        "hardware engineer",
        "электроник", "электронщик",
        "радиоэлектрон", "схемотехник",
        "embedded", "embedded developer",
        "микроконтроллер", "stm32", "arduino",
        "fpga", "плис",
        "verilog", "vhdl",
        "sdr", "dsp",
        "pcb", "altium",
        "firmware",
        "iot", "интернет вещей",
        "robotics", "робототехника",
        "circuit design"
    ],

    "Network & SysAdmin": [
        "sysadmin", "system administrator",
        "системный администратор",
        "network engineer", "сетевой инженер",
        "network", "tcp/ip",
        "linux admin", "windows server",
        "active directory",
        "voip", "asterisk",
        "nginx", "apache",
        "docker", "kubernetes", "k8s",
        "devops",
        "cloud engineer",
        "aws", "azure", "gcp",
        "virtualization", "vmware",
        "zabbix", "monitoring",
        "infrastructure"
    ],

    "Analytics & Data Science": [
        "data analyst", "аналитик данных",
        "data scientist",
        "bi analyst", "business intelligence",
        "analytics", "аналитика",
        "sql", "excel",
        "power bi", "tableau",
        "big data",
        "hadoop", "spark",
        "etl", "data pipeline",
        "data engineer",
        "математик", "статистика",
        "forecasting",
        "a/b test",
        "product analyst"
    ],

    "Software Development": [
        "developer", "разработчик",
        "программист", "software engineer",
        "backend", "frontend", "fullstack",
        "mobile developer",
        "android developer", "ios developer",
        "gamedev", "unity", "unreal",
        "web developer",
        "python developer", "java developer",
        "c#", ".net",
        "react developer",
        "microservices",
        "api development",
        "oop", "design patterns"
    ],

    "Education & HR": [
        "преподаватель", "учитель",
        "методист",
        "mentor", "наставник",
        "trainer", "обучение",
        "instructional designer",
        "recruiter", "it recruiter",
        "hr", "human resources",
        "talent acquisition",
        "hr business partner",
        "technical interviewer"
    ],

    "Support & Management": [
        "support engineer", "technical support",
        "поддержка", "helpdesk",
        "l1", "l2", "l3",
        "service desk",
        "сопровождение",
        "product manager", "project manager",
        "scrum master",
        "cto", "tech lead",
        "team lead",
        "delivery manager",
        "account manager",
        "business development"
    ]
}

PRIORITY = [
    "AI, ML & LLM",              # самая узкая и дорогая ниша
    "Cybersecurity",             # критичная и узкая
    "Electronics & Hardware",    # редкая и специфичная
    "Analytics & Data Science",  # data roles
    "QA & Automation",           # отдельная профессия
    "Network & SysAdmin",        # инфраструктура
    "Software Development",      # самая широкая категория
    "Education & HR",            # околотехнические
    "Support & Management"       # самая пересекающаяся
]
