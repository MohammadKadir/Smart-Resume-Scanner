import fitz
import os

os.makedirs("sample_resumes", exist_ok=True)

resumes = [
    {
        "filename": "sample_resumes/Md_Nasir_Alam_Java_Developer.pdf",
        "text": """MD NASIR ALAM
md.nasir.alam@email.com | +91 98765 43210 | Bengaluru, India | github.com/mdnasiralam

SUMMARY
Experienced Senior Backend Engineer with 4+ years of expertise in Java, Spring Boot, microservices architecture, and SQL database design. Proven track record in building high-performance RESTful APIs.

SKILLS
Programming: Java 17, Python, SQL, JavaScript
Frameworks: Spring Boot, Spring Data JPA, Hibernate, Express.js
Databases: PostgreSQL, MySQL, Redis, SQLite
Tools & DevOps: Git, Docker, Maven, Jenkins, REST APIs, JUnit
Concepts: Object-Oriented Programming (OOP), Microservices, Agile/Scrum

WORK EXPERIENCE
Software Engineer / Senior Backend Developer | Tech Mahindra / ABC Technologies (2022 - Present)
- Designed and developed high-throughput REST APIs using Spring Boot and Java 17.
- Optimized SQL queries in PostgreSQL, reducing database latency by 35%.
- Implemented JWT-based authentication and role-based access control.
- Managed version control with Git and built unit test suites with JUnit & Mockito.

Backend Developer | Infosys (2021 - 2022)
- Built scalable web backend components using Java and Spring framework.
- Integrated third-party payment gateways and webhook services.

EDUCATION
B.Tech in Computer Science and Engineering | National Institute of Technology (2018 - 2022)
GPA: 8.8 / 10.0
"""
    },
    {
        "filename": "sample_resumes/A_Kranthi_Frontend_Engineer.pdf",
        "text": """A. KRANTHI
a.kranthi@email.com | +91 87654 32109 | Hyderabad, India

SUMMARY
Creative Senior Frontend Developer specializing in React.js, TypeScript, and modern responsive UI development. Passionate about building fast, accessible web applications.

SKILLS
Languages: TypeScript, JavaScript (ES6+), HTML5, CSS3, SCSS
Frameworks & Libraries: React, Next.js, Redux Toolkit, Tailwind CSS, Jest
Tools: Git, Vite, Webpack, Figma, Postman

EXPERIENCE
Frontend Lead | Wipro Digital (2022 - Present)
- Built interactive recruiter and admin dashboards using React, TypeScript, and Tailwind CSS.
- Improved web application performance scores from 65 to 94 on Lighthouse.
- Implemented state management using Redux Toolkit.

EDUCATION
Bachelor of Technology in Software Engineering | JNTU Hyderabad (2018 - 2022)
"""
    },
    {
        "filename": "sample_resumes/Md_Kadir_Data_Analyst.pdf",
        "text": """MD KADIR
md.kadir@email.com | +91 76543 21098 | Pune, India

SUMMARY
Detail-oriented Data Analyst skilled in Python, SQL, Tableau, and data visualization. Experience in exploratory data analysis and executive reporting.

SKILLS
Data Tools: Python (Pandas, NumPy, Matplotlib, Seaborn), SQL, Tableau, Excel
Databases: MySQL, PostgreSQL
Concepts: Data Cleaning, A/B Testing, Business Intelligence, Statistical Analysis

WORK EXPERIENCE
Data Analyst | Analytics Insights Corp (2023 - Present)
- Conducted exploratory data analysis on 500k+ customer transactions using Python and Pandas.
- Built interactive Tableau dashboards for executive decision making.
- Wrote complex SQL queries to extract data from data warehouses.

EDUCATION
Bachelor of Science in Statistics & Economics | Pune University (2019 - 2023)
"""
    },
    {
        "filename": "sample_resumes/Ganga_Bharath_DevOps_Engineer.pdf",
        "text": """GANGA BHARATH
ganga.bharath@email.com | +91 65432 10987 | Chennai, India

SUMMARY
DevOps & Cloud Systems Engineer skilled in Docker, Kubernetes, AWS, Terraform, CI/CD pipelines, and Python automation.

SKILLS
DevOps: Docker, Kubernetes, Terraform, Ansible, Jenkins, CI/CD
Cloud & DB: AWS (EC2, S3, RDS), Linux, Bash, PostgreSQL, Python
Monitoring: Prometheus, Grafana

WORK EXPERIENCE
DevOps Engineer | CloudTech Solutions (2022 - Present)
- Configured Kubernetes clusters and containerized microservices using Docker.
- Implemented automated CI/CD pipelines using GitHub Actions and Jenkins.

EDUCATION
B.Tech in Information Technology | Anna University (2018 - 2022)
"""
    },
    {
        "filename": "sample_resumes/Priya_Sharma_Data_Scientist.pdf",
        "text": """PRIYA SHARMA
priya.sharma@email.com | +91 91234 56789 | Mumbai, India

SUMMARY
Data Scientist with experience in Machine Learning, Python, PyTorch, SQL, and Predictive Analytics.

SKILLS
AI & ML: Python, Scikit-Learn, TensorFlow, PyTorch, NLP, SQL, Pandas
Tools: Jupyter, Git, Docker, AWS SageMaker

WORK EXPERIENCE
Data Scientist | AI Innovations (2023 - Present)
- Built predictive machine learning models achieving 92% precision.

EDUCATION
M.Tech in Artificial Intelligence | IIT Bombay (2021 - 2023)
"""
    }
]

for r in resumes:
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(50, 50, 550, 800)
    page.insert_textbox(rect, r["text"], fontsize=11, fontname="helv")
    doc.save(r["filename"])
    doc.close()
    print(f"Generated {r['filename']}")
