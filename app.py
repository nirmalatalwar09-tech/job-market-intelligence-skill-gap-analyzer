import streamlit as st
import pandas as pd
import io
import plotly.express as px
import re
from io import BytesIO
from urllib.parse import quote_plus

st.set_page_config(page_title="Job Market Intelligence", page_icon="💜", layout="wide")

st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#100d1c,#19132b 55%,#24183b);color:#f8f5ff}
[data-testid="stSidebar"] {background:#201832;border-right:1px solid #493765}
h1,h2,h3,p,label,.stMarkdown {color:#f8f5ff}
[data-testid="stMetric"] {background:#2a2040;border:1px solid #594477;border-left:4px solid #a78bfa;border-radius:15px;padding:16px}
[data-testid="stMetricLabel"] {color:#d9c9f5}
[data-testid="stMetricValue"] {color:#fff}
.stButton>button {background:linear-gradient(90deg,#8b5cf6,#c4a7ff);color:#160e27;border:0;border-radius:10px;font-weight:700}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div {background:#211832!important;color:#fff!important;border-color:#665080!important}
[data-testid="stFileUploader"] {background:#281e3d;border:1px dashed #b99aff;border-radius:12px;padding:12px}
hr {border-color:#57436f}
a {color:#c4a7ff!important}
</style>
""", unsafe_allow_html=True)

PURPLE = ["#A78BFA", "#C4A7FF", "#8B5CF6", "#E9D5FF", "#6D28D9"]
st.markdown("""
<div style="padding:26px;border-radius:18px;background:linear-gradient(110deg,#291d42,#60418a);border:1px solid #a78bfa66;margin-bottom:20px">
<h1 style="margin:0;color:white">💜 Job Market Intelligence</h1>
<h3 style="margin:4px 0;color:#eadfff">& Skill Gap Analyser</h3>
<p style="margin:0;color:#f3eaff">Explore careers • Compare roles • Analyse skills • Plan your future</p>
</div>
""", unsafe_allow_html=True)

# Built-in illustrative dataset (not verified live vacancies)
JOBS_CSV = r'''Job Title,Company,Location,Salary LPA,Experience,Job Type,Skills,Job Description,Data Type
Data Analyst,TCS,Hyderabad,3.7,1-3 years,Full-time,"SQL, Data Visualization, Python, Excel, Statistics, Tableau","Illustrative Data Analyst role at TCS. Work with SQL, Data Visualization, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Infosys,Chennai,6.4,1-3 years,Full-time,"Power BI, SQL, Statistics, Tableau, Data Visualization, Python","Illustrative Data Analyst role at Infosys. Work with Power BI, SQL, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Wipro,Gurugram,4.7,1-3 years,Full-time,"Statistics, Data Visualization, Tableau, Power BI, SQL, Excel","Illustrative Data Analyst role at Wipro. Work with Statistics, Data Visualization, Tableau and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,HCLTech,Ahmedabad,4.3,Fresher,Hybrid,"Statistics, Power BI, Python, Tableau","Illustrative Data Analyst role at HCLTech. Work with Statistics, Power BI, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Tech Mahindra,Pune,6.4,0-2 years,Full-time,"SQL, Power BI, Data Visualization, Python","Illustrative Data Analyst role at Tech Mahindra. Work with SQL, Power BI, Data Visualization and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,LTIMindtree,Noida,6.5,1-3 years,Hybrid,"Power BI, Tableau, SQL, Data Visualization, Statistics, Excel","Illustrative Data Analyst role at LTIMindtree. Work with Power BI, Tableau, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Accenture,Coimbatore,8.4,0-2 years,Full-time,"Excel, Statistics, SQL, Tableau, Python, Power BI","Illustrative Data Analyst role at Accenture. Work with Excel, Statistics, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Cognizant,Pune,5.2,Fresher,Full-time,"Power BI, Python, Data Visualization, Statistics","Illustrative Data Analyst role at Cognizant. Work with Power BI, Python, Data Visualization and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Capgemini,Noida,5.6,Fresher,Hybrid,"Python, Statistics, SQL, Excel, Data Visualization, Tableau","Illustrative Data Analyst role at Capgemini. Work with Python, Statistics, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,IBM,Coimbatore,7.5,Fresher,Remote,"Statistics, Tableau, Excel, Python, SQL, Power BI","Illustrative Data Analyst role at IBM. Work with Statistics, Tableau, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Deloitte,Bengaluru,5.8,1-3 years,Remote,"SQL, Excel, Tableau, Python, Data Visualization","Illustrative Data Analyst role at Deloitte. Work with SQL, Excel, Tableau and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Amazon,Mumbai,6.3,1-3 years,Remote,"Python, Excel, Statistics, Data Visualization","Illustrative Data Analyst role at Amazon. Work with Python, Excel, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Microsoft,Kolkata,7.8,Fresher,Full-time,"Excel, Data Visualization, Tableau, Power BI, SQL","Illustrative Data Analyst role at Microsoft. Work with Excel, Data Visualization, Tableau and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Google,Hyderabad,8.5,1-3 years,Hybrid,"Excel, Statistics, Power BI, SQL, Data Visualization, Python","Illustrative Data Analyst role at Google. Work with Excel, Statistics, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Oracle,Mumbai,4.8,Fresher,Full-time,"Data Visualization, SQL, Statistics, Python, Power BI, Excel","Illustrative Data Analyst role at Oracle. Work with Data Visualization, SQL, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,SAP,Kolkata,7.8,Fresher,Hybrid,"SQL, Statistics, Python, Excel, Tableau","Illustrative Data Analyst role at SAP. Work with SQL, Statistics, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Adobe,Hyderabad,8.3,1-3 years,Full-time,"Tableau, Data Visualization, Excel, Statistics, Power BI, SQL","Illustrative Data Analyst role at Adobe. Work with Tableau, Data Visualization, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Flipkart,Chennai,3.5,Fresher,Full-time,"Python, Power BI, SQL, Tableau, Excel, Data Visualization","Illustrative Data Analyst role at Flipkart. Work with Python, Power BI, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Zoho,Gurugram,6.7,Fresher,Full-time,"Statistics, Power BI, SQL, Excel","Illustrative Data Analyst role at Zoho. Work with Statistics, Power BI, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Freshworks,Ahmedabad,6.9,1-3 years,Hybrid,"Tableau, Data Visualization, Power BI, Excel, Python","Illustrative Data Analyst role at Freshworks. Work with Tableau, Data Visualization, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Persistent Systems,Pune,3.8,0-2 years,Full-time,"Statistics, Data Visualization, Python, Power BI, Tableau","Illustrative Data Analyst role at Persistent Systems. Work with Statistics, Data Visualization, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Mphasis,Gurugram,4.4,1-3 years,Full-time,"Python, SQL, Tableau, Excel","Illustrative Data Analyst role at Mphasis. Work with Python, SQL, Tableau and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Coforge,Ahmedabad,5.9,Fresher,Hybrid,"Statistics, SQL, Excel, Data Visualization, Power BI, Tableau","Illustrative Data Analyst role at Coforge. Work with Statistics, SQL, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,Genpact,Pune,7.4,Fresher,Remote,"Power BI, Excel, Tableau, Statistics, Python, Data Visualization","Illustrative Data Analyst role at Genpact. Work with Power BI, Excel, Tableau and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Analyst,DXC Technology,Noida,5.4,0-2 years,Full-time,"SQL, Data Visualization, Power BI, Python","Illustrative Data Analyst role at DXC Technology. Work with SQL, Data Visualization, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,TCS,Coimbatore,6.6,Fresher,Full-time,"Statistics, Deep Learning, Python, Scikit-learn, SQL, Machine Learning","Illustrative Data Scientist role at TCS. Work with Statistics, Deep Learning, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Infosys,Bengaluru,11.9,Fresher,Full-time,"Pandas, SQL, Deep Learning, Statistics, Scikit-learn, Machine Learning","Illustrative Data Scientist role at Infosys. Work with Pandas, SQL, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Wipro,Mumbai,11.6,2-4 years,Full-time,"Deep Learning, Scikit-learn, Python, Statistics, Machine Learning","Illustrative Data Scientist role at Wipro. Work with Deep Learning, Scikit-learn, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,HCLTech,Coimbatore,11.8,Fresher,Full-time,"SQL, Pandas, Statistics, Scikit-learn","Illustrative Data Scientist role at HCLTech. Work with SQL, Pandas, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Tech Mahindra,Bengaluru,6.9,0-2 years,Remote,"Pandas, Python, Deep Learning, Machine Learning","Illustrative Data Scientist role at Tech Mahindra. Work with Pandas, Python, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,LTIMindtree,Mumbai,10.8,2-4 years,Full-time,"SQL, Machine Learning, Deep Learning, Python","Illustrative Data Scientist role at LTIMindtree. Work with SQL, Machine Learning, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Accenture,Kolkata,12.7,Fresher,Full-time,"Machine Learning, Python, Statistics, Pandas, Deep Learning, Scikit-learn","Illustrative Data Scientist role at Accenture. Work with Machine Learning, Python, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Cognizant,Hyderabad,5.5,0-2 years,Full-time,"Python, Scikit-learn, Deep Learning, SQL","Illustrative Data Scientist role at Cognizant. Work with Python, Scikit-learn, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Capgemini,Chennai,6.2,0-2 years,Hybrid,"Scikit-learn, Python, Deep Learning, Statistics, SQL, Machine Learning","Illustrative Data Scientist role at Capgemini. Work with Scikit-learn, Python, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,IBM,Gurugram,7.2,0-2 years,Full-time,"Machine Learning, Pandas, SQL, Deep Learning","Illustrative Data Scientist role at IBM. Work with Machine Learning, Pandas, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Deloitte,Hyderabad,9.1,Fresher,Hybrid,"Pandas, Scikit-learn, Statistics, Python","Illustrative Data Scientist role at Deloitte. Work with Pandas, Scikit-learn, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Amazon,Chennai,5.8,0-2 years,Hybrid,"Machine Learning, Python, SQL, Deep Learning","Illustrative Data Scientist role at Amazon. Work with Machine Learning, Python, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Microsoft,Gurugram,5.4,2-4 years,Full-time,"Deep Learning, Statistics, Scikit-learn, Python, Machine Learning, SQL","Illustrative Data Scientist role at Microsoft. Work with Deep Learning, Statistics, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Google,Ahmedabad,9.6,0-2 years,Hybrid,"Python, Deep Learning, Scikit-learn, SQL, Pandas","Illustrative Data Scientist role at Google. Work with Python, Deep Learning, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Oracle,Pune,12.2,0-2 years,Full-time,"Statistics, Deep Learning, Machine Learning, Pandas","Illustrative Data Scientist role at Oracle. Work with Statistics, Deep Learning, Machine Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,SAP,Noida,7.3,Fresher,Full-time,"Statistics, Pandas, Machine Learning, Python","Illustrative Data Scientist role at SAP. Work with Statistics, Pandas, Machine Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Adobe,Coimbatore,5.1,Fresher,Full-time,"Machine Learning, SQL, Pandas, Scikit-learn, Deep Learning, Python","Illustrative Data Scientist role at Adobe. Work with Machine Learning, SQL, Pandas and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Flipkart,Pune,7.1,Fresher,Full-time,"Python, Machine Learning, Scikit-learn, SQL, Pandas, Deep Learning","Illustrative Data Scientist role at Flipkart. Work with Python, Machine Learning, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Zoho,Noida,12.0,2-4 years,Remote,"SQL, Statistics, Deep Learning, Python, Scikit-learn","Illustrative Data Scientist role at Zoho. Work with SQL, Statistics, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Freshworks,Coimbatore,6.0,Fresher,Hybrid,"Statistics, SQL, Deep Learning, Scikit-learn, Python, Pandas","Illustrative Data Scientist role at Freshworks. Work with Statistics, SQL, Deep Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Persistent Systems,Bengaluru,5.4,2-4 years,Full-time,"Deep Learning, Statistics, SQL, Machine Learning, Python","Illustrative Data Scientist role at Persistent Systems. Work with Deep Learning, Statistics, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Mphasis,Mumbai,6.4,Fresher,Full-time,"SQL, Deep Learning, Pandas, Machine Learning, Statistics","Illustrative Data Scientist role at Mphasis. Work with SQL, Deep Learning, Pandas and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Coforge,Kolkata,8.8,2-4 years,Hybrid,"Machine Learning, Deep Learning, Python, Statistics, SQL","Illustrative Data Scientist role at Coforge. Work with Machine Learning, Deep Learning, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,Genpact,Hyderabad,5.4,Fresher,Remote,"Python, Machine Learning, SQL, Statistics","Illustrative Data Scientist role at Genpact. Work with Python, Machine Learning, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Data Scientist,DXC Technology,Mumbai,6.1,2-4 years,Full-time,"Statistics, Machine Learning, Pandas, Python, SQL","Illustrative Data Scientist role at DXC Technology. Work with Statistics, Machine Learning, Pandas and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,TCS,Kolkata,8.7,Fresher,Hybrid,"REST API, Python, SQL, Django, OOP, Flask","Illustrative Python Developer role at TCS. Work with REST API, Python, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Infosys,Hyderabad,5.5,2-4 years,Remote,"Flask, Git, Python, OOP, REST API, Django","Illustrative Python Developer role at Infosys. Work with Flask, Git, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Wipro,Chennai,7.5,2-4 years,Full-time,"Flask, SQL, Django, Git, REST API, OOP","Illustrative Python Developer role at Wipro. Work with Flask, SQL, Django and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,HCLTech,Gurugram,5.6,Fresher,Hybrid,"SQL, Flask, REST API, Python, Django, Git","Illustrative Python Developer role at HCLTech. Work with SQL, Flask, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Tech Mahindra,Ahmedabad,7.0,Fresher,Hybrid,"REST API, OOP, Django, Git, Flask","Illustrative Python Developer role at Tech Mahindra. Work with REST API, OOP, Django and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,LTIMindtree,Pune,4.9,2-4 years,Full-time,"Git, OOP, SQL, Flask, Python, REST API","Illustrative Python Developer role at LTIMindtree. Work with Git, OOP, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Accenture,Gurugram,8.1,2-4 years,Full-time,"Python, OOP, Django, REST API","Illustrative Python Developer role at Accenture. Work with Python, OOP, Django and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Cognizant,Ahmedabad,5.3,2-4 years,Remote,"REST API, Git, SQL, Django, Flask","Illustrative Python Developer role at Cognizant. Work with REST API, Git, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Capgemini,Pune,4.3,0-2 years,Remote,"Django, Git, Python, SQL","Illustrative Python Developer role at Capgemini. Work with Django, Git, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,IBM,Noida,7.8,Fresher,Hybrid,"SQL, Django, Python, REST API","Illustrative Python Developer role at IBM. Work with SQL, Django, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Deloitte,Coimbatore,8.4,0-2 years,Remote,"SQL, Git, OOP, REST API, Flask","Illustrative Python Developer role at Deloitte. Work with SQL, Git, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Amazon,Bengaluru,4.6,Fresher,Full-time,"Flask, Django, OOP, REST API, SQL","Illustrative Python Developer role at Amazon. Work with Flask, Django, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Microsoft,Mumbai,3.9,Fresher,Remote,"Flask, Django, OOP, SQL, Git, Python","Illustrative Python Developer role at Microsoft. Work with Flask, Django, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Google,Coimbatore,6.3,0-2 years,Remote,"Django, Git, OOP, Python, SQL, Flask","Illustrative Python Developer role at Google. Work with Django, Git, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Oracle,Bengaluru,5.3,2-4 years,Full-time,"Django, REST API, Git, Python","Illustrative Python Developer role at Oracle. Work with Django, REST API, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,SAP,Mumbai,4.6,Fresher,Remote,"Flask, REST API, Git, Django, SQL","Illustrative Python Developer role at SAP. Work with Flask, REST API, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Adobe,Kolkata,8.5,0-2 years,Full-time,"REST API, Flask, OOP, Django","Illustrative Python Developer role at Adobe. Work with REST API, Flask, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Flipkart,Hyderabad,3.8,0-2 years,Remote,"SQL, OOP, Python, Git, Flask","Illustrative Python Developer role at Flipkart. Work with SQL, OOP, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Zoho,Chennai,5.7,Fresher,Hybrid,"Python, Flask, REST API, Git","Illustrative Python Developer role at Zoho. Work with Python, Flask, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Freshworks,Gurugram,7.5,Fresher,Full-time,"Flask, REST API, OOP, Python, Django","Illustrative Python Developer role at Freshworks. Work with Flask, REST API, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Persistent Systems,Hyderabad,4.2,Fresher,Full-time,"Django, Git, Python, SQL, REST API","Illustrative Python Developer role at Persistent Systems. Work with Django, Git, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Mphasis,Chennai,8.7,2-4 years,Remote,"Django, OOP, Git, REST API, Flask, Python","Illustrative Python Developer role at Mphasis. Work with Django, OOP, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Coforge,Gurugram,6.5,Fresher,Hybrid,"Flask, OOP, Django, Python, REST API, SQL","Illustrative Python Developer role at Coforge. Work with Flask, OOP, Django and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,Genpact,Ahmedabad,7.2,Fresher,Hybrid,"Git, REST API, OOP, Django, Python, Flask","Illustrative Python Developer role at Genpact. Work with Git, REST API, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Python Developer,DXC Technology,Pune,5.2,2-4 years,Hybrid,"SQL, Python, OOP, Git, Django, Flask","Illustrative Python Developer role at DXC Technology. Work with SQL, Python, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,TCS,Noida,11.7,0-2 years,Remote,"REST API, SQL, OOP, Java","Illustrative Software Engineer role at TCS. Work with REST API, SQL, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Infosys,Coimbatore,7.2,0-2 years,Hybrid,"Python, SQL, REST API, DSA, OOP, Git","Illustrative Software Engineer role at Infosys. Work with Python, SQL, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Wipro,Pune,9.9,Fresher,Remote,"REST API, Python, Java, DSA, OOP","Illustrative Software Engineer role at Wipro. Work with REST API, Python, Java and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,HCLTech,Noida,6.5,Fresher,Hybrid,"Java, SQL, DSA, Python, OOP","Illustrative Software Engineer role at HCLTech. Work with Java, SQL, DSA and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Tech Mahindra,Coimbatore,4.2,Fresher,Remote,"DSA, Git, REST API, Java, OOP","Illustrative Software Engineer role at Tech Mahindra. Work with DSA, Git, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,LTIMindtree,Bengaluru,4.3,Fresher,Full-time,"Git, Python, SQL, REST API, OOP","Illustrative Software Engineer role at LTIMindtree. Work with Git, Python, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Accenture,Mumbai,8.0,2-4 years,Remote,"OOP, Python, DSA, Git, REST API","Illustrative Software Engineer role at Accenture. Work with OOP, Python, DSA and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Cognizant,Kolkata,5.5,0-2 years,Full-time,"Git, DSA, OOP, SQL, Python, REST API","Illustrative Software Engineer role at Cognizant. Work with Git, DSA, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Capgemini,Hyderabad,9.8,Fresher,Hybrid,"Java, OOP, Git, Python, REST API","Illustrative Software Engineer role at Capgemini. Work with Java, OOP, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,IBM,Mumbai,5.4,0-2 years,Full-time,"Git, REST API, OOP, DSA, Java, SQL","Illustrative Software Engineer role at IBM. Work with Git, REST API, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Deloitte,Kolkata,11.8,Fresher,Hybrid,"Java, OOP, Git, Python, SQL","Illustrative Software Engineer role at Deloitte. Work with Java, OOP, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Amazon,Hyderabad,7.6,0-2 years,Hybrid,"Python, OOP, SQL, Java, Git, REST API","Illustrative Software Engineer role at Amazon. Work with Python, OOP, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Microsoft,Chennai,6.9,Fresher,Full-time,"Java, DSA, SQL, REST API","Illustrative Software Engineer role at Microsoft. Work with Java, DSA, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Google,Gurugram,11.9,Fresher,Full-time,"OOP, REST API, Java, Python, Git, SQL","Illustrative Software Engineer role at Google. Work with OOP, REST API, Java and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Oracle,Ahmedabad,11.2,0-2 years,Hybrid,"REST API, SQL, Git, Python, DSA, OOP","Illustrative Software Engineer role at Oracle. Work with REST API, SQL, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,SAP,Pune,8.8,Fresher,Hybrid,"SQL, DSA, Git, Java, OOP, REST API","Illustrative Software Engineer role at SAP. Work with SQL, DSA, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Adobe,Gurugram,3.5,Fresher,Remote,"Java, Python, OOP, Git, DSA, REST API","Illustrative Software Engineer role at Adobe. Work with Java, Python, OOP and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Flipkart,Ahmedabad,5.9,2-4 years,Remote,"Git, SQL, DSA, Java, OOP, Python","Illustrative Software Engineer role at Flipkart. Work with Git, SQL, DSA and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Zoho,Pune,4.5,0-2 years,Full-time,"OOP, Python, DSA, REST API","Illustrative Software Engineer role at Zoho. Work with OOP, Python, DSA and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Freshworks,Noida,8.6,0-2 years,Hybrid,"Python, DSA, REST API, Java, SQL, OOP","Illustrative Software Engineer role at Freshworks. Work with Python, DSA, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Persistent Systems,Coimbatore,8.1,2-4 years,Remote,"Java, SQL, DSA, OOP, Python","Illustrative Software Engineer role at Persistent Systems. Work with Java, SQL, DSA and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Mphasis,Bengaluru,5.6,2-4 years,Full-time,"Git, Java, SQL, DSA","Illustrative Software Engineer role at Mphasis. Work with Git, Java, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Coforge,Mumbai,10.5,2-4 years,Full-time,"OOP, Git, REST API, Java","Illustrative Software Engineer role at Coforge. Work with OOP, Git, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,Genpact,Coimbatore,12.0,Fresher,Remote,"SQL, Git, REST API, DSA","Illustrative Software Engineer role at Genpact. Work with SQL, Git, REST API and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Software Engineer,DXC Technology,Bengaluru,6.2,0-2 years,Full-time,"REST API, SQL, Java, OOP, Python, DSA","Illustrative Software Engineer role at DXC Technology. Work with REST API, SQL, Java and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,TCS,Mumbai,14.5,3-5 years,Full-time,"TensorFlow, PyTorch, SQL, Git","Illustrative Machine Learning Engineer role at TCS. Work with TensorFlow, PyTorch, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Infosys,Kolkata,13.6,2-4 years,Full-time,"Python, TensorFlow, SQL, Scikit-learn, Git","Illustrative Machine Learning Engineer role at Infosys. Work with Python, TensorFlow, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Wipro,Hyderabad,8.6,3-5 years,Remote,"Git, Scikit-learn, PyTorch, SQL, Python, TensorFlow","Illustrative Machine Learning Engineer role at Wipro. Work with Git, Scikit-learn, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,HCLTech,Chennai,9.4,2-4 years,Remote,"PyTorch, Python, Machine Learning, TensorFlow, Git, SQL","Illustrative Machine Learning Engineer role at HCLTech. Work with PyTorch, Python, Machine Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Tech Mahindra,Gurugram,6.6,3-5 years,Full-time,"Python, SQL, Scikit-learn, Machine Learning","Illustrative Machine Learning Engineer role at Tech Mahindra. Work with Python, SQL, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,LTIMindtree,Hyderabad,13.3,3-5 years,Remote,"PyTorch, Python, Machine Learning, SQL, Scikit-learn, Git","Illustrative Machine Learning Engineer role at LTIMindtree. Work with PyTorch, Python, Machine Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Accenture,Chennai,9.6,0-2 years,Full-time,"TensorFlow, Scikit-learn, Git, PyTorch, Machine Learning, SQL","Illustrative Machine Learning Engineer role at Accenture. Work with TensorFlow, Scikit-learn, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Cognizant,Gurugram,12.7,2-4 years,Remote,"Machine Learning, Scikit-learn, SQL, Git, Python","Illustrative Machine Learning Engineer role at Cognizant. Work with Machine Learning, Scikit-learn, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Capgemini,Ahmedabad,8.0,3-5 years,Remote,"Git, Scikit-learn, TensorFlow, Python, Machine Learning","Illustrative Machine Learning Engineer role at Capgemini. Work with Git, Scikit-learn, TensorFlow and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,IBM,Pune,10.5,2-4 years,Remote,"PyTorch, Scikit-learn, Git, TensorFlow","Illustrative Machine Learning Engineer role at IBM. Work with PyTorch, Scikit-learn, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Deloitte,Noida,5.4,2-4 years,Remote,"TensorFlow, Machine Learning, SQL, PyTorch, Python","Illustrative Machine Learning Engineer role at Deloitte. Work with TensorFlow, Machine Learning, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Amazon,Coimbatore,10.0,0-2 years,Hybrid,"Git, PyTorch, SQL, Machine Learning, Scikit-learn, Python","Illustrative Machine Learning Engineer role at Amazon. Work with Git, PyTorch, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Microsoft,Pune,12.2,0-2 years,Remote,"Git, PyTorch, Python, SQL","Illustrative Machine Learning Engineer role at Microsoft. Work with Git, PyTorch, Python and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Google,Noida,5.8,3-5 years,Hybrid,"Machine Learning, Python, PyTorch, TensorFlow, Git, Scikit-learn","Illustrative Machine Learning Engineer role at Google. Work with Machine Learning, Python, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Oracle,Coimbatore,5.4,3-5 years,Full-time,"Git, Scikit-learn, PyTorch, TensorFlow, SQL, Machine Learning","Illustrative Machine Learning Engineer role at Oracle. Work with Git, Scikit-learn, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,SAP,Bengaluru,5.9,3-5 years,Full-time,"SQL, Git, TensorFlow, Machine Learning","Illustrative Machine Learning Engineer role at SAP. Work with SQL, Git, TensorFlow and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Adobe,Mumbai,5.5,0-2 years,Full-time,"SQL, Python, PyTorch, Machine Learning, TensorFlow, Scikit-learn","Illustrative Machine Learning Engineer role at Adobe. Work with SQL, Python, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Flipkart,Kolkata,9.1,3-5 years,Full-time,"TensorFlow, Git, PyTorch, Machine Learning, Python","Illustrative Machine Learning Engineer role at Flipkart. Work with TensorFlow, Git, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Zoho,Hyderabad,11.8,3-5 years,Remote,"Machine Learning, Python, Scikit-learn, PyTorch","Illustrative Machine Learning Engineer role at Zoho. Work with Machine Learning, Python, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Freshworks,Mumbai,5.1,3-5 years,Remote,"Machine Learning, Git, PyTorch, TensorFlow, SQL, Scikit-learn","Illustrative Machine Learning Engineer role at Freshworks. Work with Machine Learning, Git, PyTorch and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Persistent Systems,Kolkata,14.9,2-4 years,Hybrid,"SQL, Scikit-learn, Machine Learning, Python, Git","Illustrative Machine Learning Engineer role at Persistent Systems. Work with SQL, Scikit-learn, Machine Learning and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Mphasis,Hyderabad,13.5,2-4 years,Full-time,"PyTorch, SQL, TensorFlow, Git, Machine Learning, Python","Illustrative Machine Learning Engineer role at Mphasis. Work with PyTorch, SQL, TensorFlow and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Coforge,Chennai,8.0,3-5 years,Remote,"PyTorch, Scikit-learn, TensorFlow, SQL","Illustrative Machine Learning Engineer role at Coforge. Work with PyTorch, Scikit-learn, TensorFlow and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,Genpact,Gurugram,11.1,0-2 years,Hybrid,"Python, Scikit-learn, Git, PyTorch, Machine Learning","Illustrative Machine Learning Engineer role at Genpact. Work with Python, Scikit-learn, Git and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Machine Learning Engineer,DXC Technology,Ahmedabad,12.6,3-5 years,Full-time,"SQL, Machine Learning, Scikit-learn, TensorFlow","Illustrative Machine Learning Engineer role at DXC Technology. Work with SQL, Machine Learning, Scikit-learn and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,TCS,Pune,4.3,2-4 years,Hybrid,"Excel, Statistics, Power BI, SQL, Requirement Analysis, Communication","Illustrative Business Analyst role at TCS. Work with Excel, Statistics, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Infosys,Gurugram,8.8,2-4 years,Hybrid,"Statistics, Communication, SQL, Excel, Power BI","Illustrative Business Analyst role at Infosys. Work with Statistics, Communication, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Wipro,Ahmedabad,8.7,2-4 years,Full-time,"Requirement Analysis, Power BI, SQL, Communication, Statistics, Excel","Illustrative Business Analyst role at Wipro. Work with Requirement Analysis, Power BI, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,HCLTech,Pune,5.7,2-4 years,Remote,"Excel, SQL, Requirement Analysis, Power BI, Communication","Illustrative Business Analyst role at HCLTech. Work with Excel, SQL, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Tech Mahindra,Noida,7.5,0-2 years,Hybrid,"Power BI, Requirement Analysis, Excel, SQL","Illustrative Business Analyst role at Tech Mahindra. Work with Power BI, Requirement Analysis, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,LTIMindtree,Coimbatore,7.2,Fresher,Hybrid,"Communication, Power BI, Excel, Requirement Analysis, Statistics, SQL","Illustrative Business Analyst role at LTIMindtree. Work with Communication, Power BI, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Accenture,Bengaluru,4.3,Fresher,Full-time,"SQL, Excel, Communication, Power BI, Statistics, Requirement Analysis","Illustrative Business Analyst role at Accenture. Work with SQL, Excel, Communication and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Cognizant,Mumbai,6.2,0-2 years,Remote,"Communication, Excel, Requirement Analysis, Statistics, Power BI","Illustrative Business Analyst role at Cognizant. Work with Communication, Excel, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Capgemini,Coimbatore,5.9,2-4 years,Hybrid,"Statistics, SQL, Communication, Power BI, Excel, Requirement Analysis","Illustrative Business Analyst role at Capgemini. Work with Statistics, SQL, Communication and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,IBM,Bengaluru,9.2,0-2 years,Hybrid,"Statistics, Power BI, SQL, Communication","Illustrative Business Analyst role at IBM. Work with Statistics, Power BI, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Deloitte,Mumbai,5.2,0-2 years,Full-time,"Statistics, Power BI, Requirement Analysis, Excel","Illustrative Business Analyst role at Deloitte. Work with Statistics, Power BI, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Amazon,Kolkata,9.4,Fresher,Full-time,"Excel, SQL, Statistics, Communication, Requirement Analysis","Illustrative Business Analyst role at Amazon. Work with Excel, SQL, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Microsoft,Hyderabad,8.1,0-2 years,Full-time,"Requirement Analysis, SQL, Statistics, Excel","Illustrative Business Analyst role at Microsoft. Work with Requirement Analysis, SQL, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Google,Chennai,8.7,2-4 years,Full-time,"SQL, Statistics, Power BI, Excel, Communication","Illustrative Business Analyst role at Google. Work with SQL, Statistics, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Oracle,Gurugram,5.1,Fresher,Full-time,"Power BI, SQL, Statistics, Excel","Illustrative Business Analyst role at Oracle. Work with Power BI, SQL, Statistics and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,SAP,Hyderabad,8.2,0-2 years,Full-time,"Communication, Requirement Analysis, Excel, Power BI, Statistics, SQL","Illustrative Business Analyst role at SAP. Work with Communication, Requirement Analysis, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Adobe,Chennai,7.4,0-2 years,Full-time,"Requirement Analysis, SQL, Excel, Power BI, Statistics","Illustrative Business Analyst role at Adobe. Work with Requirement Analysis, SQL, Excel and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Flipkart,Gurugram,6.4,Fresher,Remote,"Communication, Statistics, Requirement Analysis, Power BI","Illustrative Business Analyst role at Flipkart. Work with Communication, Statistics, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Zoho,Ahmedabad,5.2,Fresher,Hybrid,"Excel, Power BI, SQL, Statistics","Illustrative Business Analyst role at Zoho. Work with Excel, Power BI, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Freshworks,Pune,8.3,Fresher,Full-time,"Requirement Analysis, Statistics, Power BI, SQL, Communication","Illustrative Business Analyst role at Freshworks. Work with Requirement Analysis, Statistics, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Persistent Systems,Noida,5.5,0-2 years,Remote,"Statistics, Requirement Analysis, SQL, Communication, Power BI, Excel","Illustrative Business Analyst role at Persistent Systems. Work with Statistics, Requirement Analysis, SQL and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Mphasis,Coimbatore,5.0,2-4 years,Full-time,"Communication, Excel, Power BI, SQL, Statistics","Illustrative Business Analyst role at Mphasis. Work with Communication, Excel, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Coforge,Pune,8.0,Fresher,Hybrid,"Communication, Excel, Requirement Analysis, Statistics, Power BI, SQL","Illustrative Business Analyst role at Coforge. Work with Communication, Excel, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,Genpact,Noida,6.0,Fresher,Remote,"Requirement Analysis, Excel, Power BI, Communication","Illustrative Business Analyst role at Genpact. Work with Requirement Analysis, Excel, Power BI and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
Business Analyst,DXC Technology,Coimbatore,7.4,Fresher,Full-time,"Excel, Power BI, Requirement Analysis, SQL, Statistics, Communication","Illustrative Business Analyst role at DXC Technology. Work with Excel, Power BI, Requirement Analysis and collaborate with the team on business and technology projects.",Illustrative sample - not a verified current vacancy
'''

df = pd.read_csv(io.StringIO(JOBS_CSV))
df["Salary LPA"] = pd.to_numeric(df["Salary LPA"], errors="coerce")

# Sidebar and optional CSV upload
st.sidebar.title("💜 Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Compare Roles", "Skill Gap & Roadmap", "Resume Analyser", "Find Jobs Online", "Project Ideas", "About Project"])
uploaded_csv = st.sidebar.file_uploader("Optional: replace built-in dataset (CSV)", type=["csv"])
if uploaded_csv is not None:
    try:
        custom = pd.read_csv(uploaded_csv)
        needed = {"Job Title", "Location", "Salary LPA", "Skills"}
        if needed.issubset(custom.columns):
            df = custom.copy()
            for col, default in {"Company": "Uploaded company", "Experience": "Not specified", "Job Description": ""}.items():
                if col not in df.columns:
                    df[col] = default
            df["Salary LPA"] = pd.to_numeric(df["Salary LPA"], errors="coerce")
            st.sidebar.success("Your dataset is loaded.")
        else:
            st.sidebar.error("CSV needs Job Title, Location, Salary LPA and Skills columns.")
    except Exception as exc:
        st.sidebar.error(f"Could not read CSV: {exc}")

# Clean required columns and prepare role lists
for col, default in {"Job Title": "Unknown role", "Company": "Company not specified", "Location": "Not specified", "Salary LPA": 0, "Skills": "", "Experience": "Not specified", "Job Description": ""}.items():
    if col not in df.columns:
        df[col] = default
df["Skills"] = df["Skills"].fillna("").astype(str)
df["Job Title"] = df["Job Title"].fillna("Unknown role").astype(str)
df["Location"] = df["Location"].fillna("Not specified").astype(str)
roles = sorted(df["Job Title"].dropna().unique().tolist())
if not roles:
    roles = ["Data Analyst"]
role_skills = {}
for r in roles:
    values = df.loc[df["Job Title"] == r, "Skills"]
    role_skills[r] = sorted({skill.strip() for value in values for skill in str(value).split(",") if skill.strip()})

skill_bank = sorted({skill for skills in role_skills.values() for skill in skills} | {"Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "Data Visualization", "Machine Learning", "Deep Learning", "Pandas", "Scikit-learn", "TensorFlow", "Java", "Git", "APIs", "Django", "MongoDB", "Communication", "DAX", "OOP"})

# OVERVIEW
if page == "Overview":
    st.subheader("📊 Job Market Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jobs listed", len(df))
    c2.metric("Job roles", df["Job Title"].nunique())
    avg_salary = df["Salary LPA"].mean()
    c3.metric("Average salary", f"{avg_salary:.1f} LPA" if pd.notna(avg_salary) else "N/A")
    c4.metric("Locations", df["Location"].nunique())
    query = st.text_input("Search job title, company or skill")
    locations = ["All"] + sorted(df["Location"].dropna().unique().tolist())
    location = st.selectbox("Filter by location", locations)
    view = df.copy()
    if query:
        view = view[view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)]
    if location != "All":
        view = view[view["Location"] == location]
    st.dataframe(view, use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        counts = pd.Series([skill.strip() for cell in df["Skills"] for skill in str(cell).split(",") if skill.strip()]).value_counts().head(10).rename_axis("Skill").reset_index(name="Job Count")
        if not counts.empty:
            st.plotly_chart(px.bar(counts, x="Job Count", y="Skill", orientation="h", title="Most in-demand skills", color="Job Count", color_continuous_scale="Purples"), use_container_width=True)
    with right:
        salary_data = df.groupby("Job Title", as_index=False)["Salary LPA"].mean().sort_values("Salary LPA")
        st.plotly_chart(px.bar(salary_data, x="Job Title", y="Salary LPA", title="Average sample salary by role", color="Salary LPA", color_continuous_scale="Purples"), use_container_width=True)
    st.caption("All built-in records and salary figures are illustrative sample data, not verified current vacancies or salary benchmarks.")

# ROLE COMPARISON
elif page == "Compare Roles":
    st.subheader("⚖️ Compare Job Roles")
    chosen = st.multiselect("Choose roles to compare", roles, default=roles[:min(3, len(roles))])
    comparison = df[df["Job Title"].isin(chosen)]
    if not comparison.empty:
        summary = comparison.groupby("Job Title").agg(Companies=("Company", "nunique"), Average_Salary=("Salary LPA", "mean"), Jobs=("Job Title", "size")).reset_index()
        st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(summary, x="Job Title", y="Average_Salary", color="Job Title", title="Average sample salary comparison", color_discrete_sequence=PURPLE), use_container_width=True)
        for selected_role in chosen:
            with st.expander(f"{selected_role} — required skills"):
                st.write(", ".join(role_skills.get(selected_role, [])) or "No skills listed")
    else:
        st.info("Select at least one role to compare.")

# SKILL GAP AND ROADMAP
elif page == "Skill Gap & Roadmap":
    st.subheader("🎯 Find Your Skill Gaps")
    target_role = st.selectbox("Select your target role", roles)
    known = st.multiselect("Select skills you already know", skill_bank)
    required = role_skills.get(target_role, [])
    matched = sorted(set(known) & set(required))
    missing = sorted(set(required) - set(known))
    score = round(100 * len(matched) / len(required)) if required else 0
    st.metric("Your skill match", f"{score}%")
    st.progress(score / 100)
    left, right = st.columns(2)
    left.success("Matched: " + (", ".join(matched) if matched else "None selected"))
    right.warning("Skills to learn: " + (", ".join(missing) if missing else "No gaps found"))
    st.markdown("### 🗺️ Suggested learning roadmap")
    if missing:
        for index, skill in enumerate(missing, 1):
            st.write(f"{index}. Learn **{skill}** — study the basics, practise with a small task, then add it to a project.")
    else:
        st.info("Great! Select another target role or add more skills to explore.")
    st.caption("Match percentage is based on keyword overlap with the selected role's sample job listings.")

# RESUME ANALYSER
elif page == "Resume Analyser":
    st.subheader("📄 Resume Skill Analyser")
    target_role = st.selectbox("Choose target job role", roles)
    resume = st.file_uploader("Upload resume (PDF or DOCX)", type=["pdf", "docx"])
    if resume is not None:
        try:
            if resume.name.lower().endswith(".pdf"):
                import fitz
                pdf = fitz.open(stream=resume.getvalue(), filetype="pdf")
                resume_text = " ".join(page.get_text() for page in pdf)
            else:
                from docx import Document
                document = Document(BytesIO(resume.getvalue()))
                resume_text = " ".join(paragraph.text for paragraph in document.paragraphs)
            found = [skill for skill in skill_bank if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", resume_text, re.I)]
            required = role_skills.get(target_role, [])
            found_lower = {skill.lower() for skill in found}
            matched = [skill for skill in required if skill.lower() in found_lower]
            missing = [skill for skill in required if skill.lower() not in found_lower]
            score = round(100 * len(matched) / len(required)) if required else 0
            st.metric("Resume skill match", f"{score}%")
            st.progress(score / 100)
            st.write("**Skills found:**", ", ".join(found) if found else "No recognised skills found")
            st.success("**Role skills matched:** " + (", ".join(matched) if matched else "None"))
            st.warning("**Skills missing for this role:** " + (", ".join(missing) if missing else "None"))
            st.info("This is a keyword-based check, not an AI judgement of your resume.")
        except Exception as exc:
            st.error(f"Could not read resume: {exc}. Check that the required PDF/DOCX package is installed.")
    else:
        st.info("Upload a PDF or DOCX resume to check its skills.")

# FIND JOBS ONLINE
elif page == "Find Jobs Online":
    st.subheader("🔎 Find Jobs on Job Websites")
    st.write("Search for current vacancies directly on popular job websites.")
    job_role = st.selectbox("Select job role", roles)
    job_location = st.text_input("Preferred location", "Hyderabad")
    keywords = st.text_input("Additional keywords (optional)", "")
    search_text = " ".join(part for part in [job_role, keywords, job_location] if part.strip())
    encoded = quote_plus(search_text)
    indeed_query = quote_plus(" ".join(part for part in [job_role, keywords] if part.strip()))
    location_encoded = quote_plus(job_location)
    st.markdown("### Search vacancies")
    st.markdown(f"""
    <div style="background:#2a2040;border:1px solid #8064a8;border-radius:14px;padding:18px;margin:10px 0">
      <h3>🔵 LinkedIn Jobs</h3><p>Search job vacancies, companies and locations.</p>
      <a href="https://www.linkedin.com/jobs/search/?keywords={encoded}" target="_blank">Search on LinkedIn ↗</a>
    </div>
    <div style="background:#2a2040;border:1px solid #8064a8;border-radius:14px;padding:18px;margin:10px 0">
      <h3>🟠 Indeed India</h3><p>Browse matching job advertisements.</p>
      <a href="https://in.indeed.com/jobs?q={indeed_query}&l={location_encoded}" target="_blank">Search on Indeed ↗</a>
    </div>
    <div style="background:#2a2040;border:1px solid #8064a8;border-radius:14px;padding:18px;margin:10px 0">
      <h3>🟢 Naukri</h3><p>Find Indian IT and fresher job opportunities.</p>
      <a href="https://www.naukri.com/{quote_plus(job_role.lower().replace(' ', '-'))}-jobs-in-{location_encoded.lower()}" target="_blank">Search on Naukri ↗</a>
    </div>
    """, unsafe_allow_html=True)
    st.info("These buttons open external job websites. Their listings and availability are controlled by those websites.")
    st.caption("The dashboard's built-in dataset is for analysis and demonstration. Use these links to view current vacancies.")

# PORTFOLIO PROJECT IDEAS
elif page == "Project Ideas":
    st.subheader("💼 Top 5 Portfolio Projects")
    target_role = st.selectbox("Choose your target job role", roles)
    project_ideas = {
        "Data Analyst": [
            ("E-commerce Sales Dashboard", "Analyse sales, revenue and profit.", "Power BI, SQL, Excel"),
            ("Customer Churn Analysis", "Identify customers likely to leave.", "Python, Pandas, SQL"),
            ("HR Analytics Dashboard", "Analyse employee performance and attrition.", "Power BI, Excel"),
            ("Banking Customer Analysis", "Study customer transactions and behaviour.", "Python, SQL"),
            ("Job Market Trends Dashboard", "Analyse salaries, job roles and skills.", "Python, Streamlit, Plotly")],
        "Data Scientist": [
            ("House Price Prediction", "Predict house prices using ML.", "Python, Scikit-learn"),
            ("Customer Segmentation", "Group customers using clustering.", "Python, K-Means"),
            ("Loan Default Prediction", "Predict loan repayment risk.", "Python, ML"),
            ("Sales Forecasting", "Predict future sales.", "Python, Pandas"),
            ("Sentiment Analysis", "Analyse customer reviews.", "Python, NLP")],
        "Python Developer": [
            ("Student Management System", "Manage student records.", "Python, SQL"),
            ("Expense Tracker", "Track income and expenses.", "Python, Streamlit"),
            ("Weather Application", "Display weather information.", "Python, API"),
            ("Library Management System", "Manage books and members.", "Python, SQLite"),
            ("CSV Report Generator", "Generate automated reports.", "Python, Pandas")],
        "Business Analyst": [
            ("Retail Performance Dashboard", "Analyse retail business performance.", "Excel, Power BI"),
            ("Customer Feedback Analysis", "Understand customer satisfaction.", "Python, Excel"),
            ("Sales KPI Dashboard", "Track business performance.", "Power BI, SQL"),
            ("Supply Chain Analysis", "Analyse delivery and inventory.", "SQL, Excel"),
            ("Banking Data Analysis", "Study banking customer behaviour.", "Python, Power BI")],
        "Machine Learning Engineer": [
            ("Resume Skill Extractor", "Extract skills from resumes.", "Python, NLP"),
            ("Image Classification", "Classify uploaded images.", "Python, TensorFlow"),
            ("House Price Prediction", "Build a prediction model.", "Python, Scikit-learn"),
            ("Customer Churn Prediction", "Predict customer churn.", "Python, ML"),
            ("Model Deployment System", "Deploy an ML model using an API.", "Python, FastAPI")]
    }
    ideas = project_ideas.get(target_role, [
        ("Job Portal Application", "Build a job search application.", "Python, SQL"),
        ("Data Analysis Dashboard", "Analyse a real-world dataset.", "Python, Power BI"),
        ("Automation Application", "Automate repetitive tasks.", "Python"),
        ("Database Management System", "Create a database application.", "SQL, Python"),
        ("Portfolio Website", "Showcase your skills and projects.", "HTML, CSS, JavaScript")])
    for index, (title, description, technologies) in enumerate(ideas, 1):
        with st.expander(f"⭐ {index}. {title}"):
            st.write(description)
            st.write(f"**Technologies:** {technologies}")
            st.write("**Portfolio tip:** Upload your source code and README to GitHub.")

# ABOUT PROJECT
elif page == "About Project":
    st.subheader("ℹ️ Project Methodology")
    st.write("**Goal:** Help students and job seekers explore job roles, compare required skills, identify skill gaps and plan portfolio development.")
    st.markdown("""
    **How it works**
    1. Load the built-in sample job dataset or upload a CSV.
    2. Clean and organise job role, salary, location and skill fields.
    3. Count repeated skills to identify demand patterns.
    4. Compare selected roles using average sample salary and skill lists.
    5. Compare user-selected or resume-extracted skills with role requirements.
    6. Generate a simple learning roadmap and portfolio project suggestions.
    """)
    st.markdown("**Technologies:** Python, Streamlit, Pandas, Plotly, PyMuPDF and python-docx.")
    st.markdown("**Data sources:** Built-in illustrative sample records and optional user-uploaded CSV. Job portal links open external searches.")
    st.warning("The included job records are illustrative sample data, not verified live vacancies or a complete labour-market survey.")
    st.markdown("**Future enhancements:** Connect verified job APIs, add a larger regularly updated dataset, improve resume parsing and personalise learning resources.")

st.markdown("---")
st.caption("💜 Job Market Intelligence & Skill Gap Analyser | Student Project Demo | Midnight Lavender Purple")
