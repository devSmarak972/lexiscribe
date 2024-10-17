
from fpdf import FPDF
import os
from datetime import datetime
import re
language_setting={
	"Hindi":"hin_Deva",
	"Bengali":"ben_Beng",
	"Assamese":"asm_Beng",
	"Nepali":"npi_Deva",
	"Bodo":"brx_Deva",
	"Manipuri":"mni_Beng",
	# "Manipuri (Meitei)":"mni_Mtei"
}
def getDate(date_str):
	print(date_str)
	date_str=date_str.strip()
	# Parse the date string
	# parsed_date = datetime.strptime(date_str, '%Y')
	# Convert to the desired string format, e.g., "March 4, 1975"
	# formatted_date = parsed_date.strftime('%Y')
	return 

def createPDF(case, language, content):
	# Define the filename for the PDF
	pdf_filename = f"{case}_{language}.pdf"
	
	pdf_path = os.path.join(os.getcwd(), "pdfs", pdf_filename)
	if os.path.exists(pdf_path):
		os.remove(pdf_path)

	# Ensure the directory exists
	os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

	# Create a PDF instance
	pdf = FPDF()
	pdf.add_page()

	# Register and set the font based on the language
	pdf.add_font('NotoSerifBold', '', os.path.join(os.getcwd(), "fonts", 'NotoSerif-Bold.ttf'), uni=True)
	if language == 'English':
		# Set the English font
		pdf.add_font('NotoSerif', '', os.path.join(os.getcwd(), "fonts", 'NotoSerif-Regular.ttf'), uni=True)
		pdf.set_font('NotoSerif', '', 12)
		f='NotoSerif'
		sep = "."
	elif language in ['Bengali','Manipuri','Assamese']:
		# Set the Bengali font
		pdf.add_font('NotoSansBengali', '', os.path.join(os.getcwd(), "fonts", 'NotoSansBengali-Regular.ttf'), uni=True)
		# pdf.add_font('NotoSansBengali', '', os.path.join(settings.MEDIA_ROOT, "fonts", 'NotoSansBengali-Regular.ttf'), uni=True)
		pdf.set_font('NotoSansBengali', '', 12)
		f='NotoSansBengali'
		sep = "|"
	elif language in ['Hindi','Bodo','Nepali']:
		# Set the Hindi font
		pdf.add_font('NotoSansDevanagari', '', os.path.join(os.getcwd(), "fonts", 'NotoSansDevanagari-Regular.ttf'), uni=True)
		pdf.set_font('NotoSansDevanagari', '', 12)
		f='NotoSansDevanagari'
		sep = "|"
	
	# Process the content and add it to the PDF
	for line in content.split("\n\n"):
		heading = re.findall(r'\*(.*?)\*', line)
		if len(heading)==0:
			continue
		heading=heading[0]
		# print(heading,"heading")
		pdf.set_font("NotoSerifBold", '', 14)
		pdf.multi_cell(0, 14, heading,ln=True)
		line=line[len(heading)+3:]
		# print(line)
		pdf.set_font(f, '', 12)
		pdf.multi_cell(0, 10, line)
		pdf.ln(5)  # Add some space between paragraphs

	# print(content)
	# print("=======================")
	# Output the PDF to a file
	pdf.output(pdf_path)

	# Return the path to the PDF
	return pdf_filename



def getSections(content):
	# Regex pattern to match headings and their content
	pattern = re.compile(r'###\s*(.*?):(.*?)(?=###|$)', re.DOTALL)

	# Dictionary to store headings and their corresponding content
	sections = {}

	# Find all matches of headings and their content
	matches = pattern.findall(content)

	# Store each heading and content in the dictionary
	for match in matches:
		
		heading = match[0].strip()  # Heading text (without **)
		content = match[1].strip()  # Content associated with the heading
		if content=="":
			continue
		sections[heading] = content.replace("*","-")
	return sections
import pickle
def readFile(case,language):
	case_root=os.path.join(os.getcwd(), "files")
	case_lang_root=os.path.join(os.getcwd(), "data")
	# Construct the filename
	# language="English"
	if language!="English":
		try:

			content=pickle.load(open(os.path.join(case_lang_root,f"data.pkl"),"rb"))
			content=content[case]
			# print(content)
			content={section:value[language_setting[language]] for section,value in content.items()}
			
			if language in ["Bengali","Hindi"]:
				text=""
				for section,value in content.items():
					text+=section+"\n"+value+"\n\n"
				pdf=createPDF(case,language,text)
			else:
				filename = f"Summ_English.txt"
				file_path = os.path.join(case_root, case,filename)
				# Read the contents of the file
				try:
					with open(file_path, 'r', encoding="utf-8") as file:
						text = file.read()
					pdf=createPDF(case,"English",text)
				except Exception as e:
					# Handle any other exceptions
					# content = None
					print(f"An error occurred: {e}")
			return content
		except Exception as e:
			content=None
			print("Error",e)
			return content

	filename = f"Summ_{language}.txt"
	# Construct the full file path
	file_path = os.path.join(case_root, case,filename)
	print(language)
	# Read the contents of the file
	try:
		with open(file_path, 'r', encoding="utf-8") as file:
			content = file.read()
		# pdf=createPDF(case,language,content)

	except FileNotFoundError:
		# Handle the case where the file does not exist
		content = None
	except Exception as e:
		# Handle any other exceptions
		content = None
		print(f"An error occurred: {e}")
	
	return getSections(content)

cases={
	# "MANU_SC_1967_0029":"The Constitution (Forty-Fourth Amendment) Act 1978 and The Constitution (Forty-Fifth Amendment) Act 2002",
"MANU_SC_1975_0304":"Kesavananda Bharati v. State of Kerala",
"MANU_SC_1978_0133":"Passport Authority v. Government of India",
# "MANU_SC_1983_0382":"State of Maharashtra vs. The Director General of Police and others",
"MANU_SC_1985_0039":"Bombay High Court and Supreme Court Judgments on Right to Life and Livelihood",
"MANU_SC_1986_0716":"K.P. Joseph v. State of Kerala & Ors.",
"MANU_SC_1993_0333":"TMA Pai Foundation vs. State of Karnataka and Ors. ( implications on Education Regulation and Affiliation)",
"MANU_SC_1995_0290":"Mohamed Ahmed Khan v. Shah Bano Begum and others",
"MANU_SC_1997_0157":"Nilabati Behera vs. State of Orissa (1993) and various other cases",
"MANU_SC_1997_0261":"Tribunals' Competence to Test Constitutional Validity of Statutory Provisions/Rules",
"MANU_SC_2002_0189":"State of Punjab v. Span Motels Pvt. Ltd",
"MANU_SC_2002_0394":"Election Commission of India v. Subramanian Swamy",
"MANU_SC_2002_1141":"Lawyers' Right to Strike: Supreme Court of India",
"MANU_SC_2006_0399":"President of India & Ors v. Speaker, Bihar Legislative Assembly & Ors.",
"MANU_SC_2008_3096":"State of Maharashtra v. Bombay High Court",
"MANU_SC_2010_0325":"Supreme Court of India vs. Narcoanalysis, Polygraph Examination, and Brain Electro-Stimulation (BEAP) Test",
"MANU_SC_2011_0176":"Aruna Shanbaug's Right to Die with Dignity",
"MANU_SC_2012_0311":"Supreme Court of India vs. Unaided Private Schools",      
"MANU_SC_2015_0329":"Shreya Singhal v. Union of India (2015) 10 SCC 459"}

casesdict={key:{"name":value,"date":key[8:12]} for key,value in sorted(cases.items())}
def main(case_num,lang):
	global casesdict
	filename = f"Summ_English.txt"
	case_root=os.path.join(os.getcwd(), "files")

	file_path = os.path.join(case_root, case_num,filename)
	# Read the contents of the file
	with open(file_path, 'r', encoding="utf-8") as file:
		text = file.read()
	eng_sections=getSections(text)
	print(eng_sections)
	if lang!="English":
		ret=readFile(case_num,lang)
	else:
		ret=eng_sections
	# print(ret,case_num,lang)
	ret["Case Type"]=[it.strip() for it in eng_sections["Case Type"].split(",")]
	ret["Case name"]=eng_sections["Case name"]
	# reordering-----
	# order=["Case name","Case Type","Case","Summary","Main Arguments","Court Decisions","Arguments by Plaintiff","Arguments by Defendant","Legal Precedents or Statutes Cited","Quotations from the court","Judgement","Conclusion"]
	order=["Case name","Case Type","Case","Brief Summary","Main Arguments","Legal Precedents or Statutes Cited","Quotations from the court","Present Court's Verdict","Conclusion"]
	# reordering-----
	ret["Case name"]=casesdict[case_num]["name"]+" ("+case_num[8:12]+")"
	ret["Brief Summary"]=ret.pop("Summary")
	ret["Present Court's Verdict"]=ret.pop("Court Decisions")
	text=""
	ret = {key: ret[key] for key in order if key in ret.keys()}
	# if lang in ["English","Bengali","Hindi"]:
		# print("=======================================")
	for section,value in ret.items():
			if section.lower()=="case type":
				continue
			# print(section,value)
			text+="*"+section+"*"+"\n"+value+"\n\n"
	pdf=createPDF(case_num,lang,text)
	# else:
	# 	for section,value in ret.items():
	# 			if section.lower()=="case type":
	# 				continue
	# 			# print(section,value)
	# 			text+=section+"\n"+value+"\n\n"
	# 	default_lang="English"
	# 	pdf=createPDF(case_num,default_lang,text)


	# print("=======================================")
	ret = {key.lower(): ret[key] for key in ret.keys()}
	return ret
	context={"success":True,"output":ret,"form_submitted":True,"language":lang,"selected_case":case_num,"cases":casesdict}
	# return redirect('/?submitted=True')
master_dict={}
for case in cases.keys():
	master_dict[case]={}
	for lang in language_setting.keys():
		data=main(case,lang)
		master_dict[case][lang]=data
import json
# Save the dictionary as a JSON file
with open("data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)
