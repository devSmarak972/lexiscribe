from django.shortcuts import render,redirect
from groq import Groq
from legal_text import settings
from django.core.files.storage import FileSystemStorage
from pypdf import PdfReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
MAX_TOKENS=500
# from nltk.tokenize import word_tokenize,sent_tokenize
# from .indicTrans import initialize_model_and_tokenizer, batch_translate
from .cleanJudgement import clean_judgment
quantization = None
model_id = "ai4bharat/indictrans2-en-indic-1B"  # ai4bharat/indictrans2-en-indic-dist-200M
en_indic_ckpt_dir=settings.MODEL_DIR
# en_indic_tokenizer, en_indic_model = initialize_model_and_tokenizer(model_id,en_indic_ckpt_dir, "en-indic", quantization)
language_setting={
	"Hindi":"hin_Deva",
	"Bengali":"ben_Beng",
	"Assamese":"asm_Beng",
	"Nepali":"npi_Deva",
	"Bodo":"brx_Deva",
	# "Manipuri":"mni_Beng",
	# "Manipuri (Meitei)":"mni_Mtei"
}
code_to_lang = {v: k for k, v in language_setting.items()}

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.fonts import tt2ps
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfgen import canvas
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import default_storage
def split_text_into_sentences(text):
	sentences = sent_tokenize(text)
	return sentences

# def indicTranslate(in_text,out_lang):
# 	src_lang, tgt_lang = "eng_Latn", language_setting[out_lang]
# 	en_sents=split_text_into_sentences(in_text)
# 	print(en_sents)
# 	hi_translations = batch_translate(en_sents, src_lang, tgt_lang, en_indic_model, en_indic_tokenizer)
# 	print(f"\n{src_lang} - {tgt_lang}")
# 	ret=""
# 	for input_sentence, translation in zip(en_sents, hi_translations):
# 		print(f"{src_lang}: {input_sentence}")
# 		print(f"{tgt_lang}: {translation}")
# 		ret+=translation+" "
# 	return ret

from fpdf import FPDF
import os
from datetime import datetime

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
	pdf_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_filename)
	if os.path.exists(pdf_path):
		os.remove(pdf_path)

	# Ensure the directory exists
	os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

	# Create a PDF instance
	pdf = FPDF()
	pdf.add_page()

	# Register and set the font based on the language
	if language == 'English':
		# Set the English font
		pdf.add_font('NotoSerif', '', os.path.join(settings.MEDIA_ROOT, "fonts", 'NotoSerif-Regular.ttf'), uni=True)
		pdf.set_font('NotoSerif', '', 12)
		sep = "."
	elif language in ['Bengali','Manipuri']:
		# Set the Bengali font
		pdf.add_font('NotoSansBengali', '', os.path.join(settings.MEDIA_ROOT, "fonts", 'NotoSansBengali-Regular.ttf'), uni=True)
		pdf.set_font('NotoSansBengali', '', 12)
		sep = "|"
	elif language in ['Hindi','Bodo','Nepali']:
		# Set the Hindi font
		pdf.add_font('NotoSansDevanagari', '', os.path.join(settings.MEDIA_ROOT, "fonts", 'NotoSansDevanagari-Regular.ttf'), uni=True)
		pdf.set_font('NotoSansDevanagari', '', 12)
		sep = "|"
	
	# Process the content and add it to the PDF
	for line in content.split("\n\n"):
		pdf.multi_cell(0, 10, line)
		pdf.ln(5)  # Add some space between paragraphs

	# print(content)
	# print("=======================")
	# Output the PDF to a file
	pdf.output(pdf_path)

	# Return the path to the PDF
	return pdf_filename

# def createPDF(case,language,content):
# 	# Define the filename for the PDF
# 	pdf_filename = f"{case}_{language}.pdf"
# 	pdf_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_filename)

# 	# Ensure the directory exists
# 	os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

# 	# Create a PDF with the content
# 	# c = canvas.Canvas(pdf_path, pagesize=letter)
# 	width, height = letter
# # Register the fonts
# 	pdfmetrics.registerFont(TTFont('Noto-Serif', os.path.join(settings.MEDIA_ROOT,"fonts",'NotoSerif-Regular.ttf')))
# 	pdfmetrics.registerFont(TTFont('Noto-Sans-Bengali', os.path.join(settings.MEDIA_ROOT,"fonts",'NotoSansBengali-Regular.ttf')))
# 	pdfmetrics.registerFont(TTFont('Noto-Sans-Devanagari', os.path.join(settings.MEDIA_ROOT,"fonts",'NotoSansDevanagari-Regular.ttf')))

# 	# Add the content to the PDF
# 	# text_object = c.beginText(40, height - 40)
# 	# Create the PDF document
# 	doc = SimpleDocTemplate(pdf_path, pagesize=letter)

# 	# Get the sample style sheet
# 	styles = getSampleStyleSheet()
#  # Optional: Adjust other style properties
# 	styles['Normal'].fontSize = 12
# 	styles['Normal'].alignment = TA_JUSTIFY  # Justified text

#  # Determine the font based on language
# 	if language == 'English':
# 		# c.setFont('Noto-Serif', 12)
# 		styles['Normal'].fontName='Noto-Serif'
# 		sep="."
# 	elif language == 'Bengali':
# 		styles['Normal'].fontName='Noto-Sans-Bengali'
# 		# c.setFont('Noto-Sans-Bengali', 12)
# 		sep="|"
# 	elif language == 'Hindi':
# 		styles['Normal'].fontName='Noto-Sans-Hindi'
# 		# c.setFont('Noto-Sans-Devanagari', 12)
# 		sep="|"
	

# 	 # Create a list to hold the PDF elements
# 	story = []

# 	for line in content.split("\n\n"):
# 		story.append(Paragraph(line, styles['Normal']))
# 		story.append(Spacer(1, 12))  # Add space between paragraphs

# 		# text_object.textLine(line)
# 	doc.build(story)

# 	# c.drawText(text_object)
# 	# c.save()

# 	# Return the path to the PDF
# 	return pdf_filename

def count_tkn_with_tokenizer(txt: str) -> int:
	return len(word_tokenize(txt))
# Load the tokenizer

# import spacy
# !python -m spacy download en_core_web_lg --quiet
# nlp = spacy.load("en_core_web_lg")


def create_chunks (sentences, doc_chunk_len: int = 484):
	max_chunk_token_len = doc_chunk_len

	chunks = []
	current_chunk_tkn_len = 0
	current_chunk = ""

	for sentence in sentences:
		word_tkn_len = count_tkn_with_tokenizer(sentence)

		if current_chunk_tkn_len + word_tkn_len < max_chunk_token_len:
			current_chunk += str(sentence + " ")
			current_chunk_tkn_len += word_tkn_len
		else:
			chunks.append(current_chunk.strip())
			current_chunk = str(sentence + " ")
			current_chunk_tkn_len = word_tkn_len

	if current_chunk:
		chunks.append(current_chunk.strip())

	return chunks


import os
# models={
# 	"Llama3":"llama3-8b-8192",
# 	"Mixtral":"mixtral-8x7b-32768"
# }
models = {
	"Distil-Whisper English": "distil-whisper-large-v3-en",
	"Gemma 2 9B": "gemma2-9b-it",
	"Gemma 7B": "gemma-7b-it",
	"Llama 3.1 70B": "llama-3.1-70b-versatile",
	"Llama 3.1 8B": "llama-3.1-8b-instant",
	"Llama Guard 3 8B": "llama-guard-3-8b",
	"Llama 3 70B": "llama3-70b-8192",
	"Llama 3 8B": "llama3-8b-8192",
	"Mixtral 8x7B": "mixtral-8x7b-32768",
	"Whisper": "whisper-large-v3"
}



cases={
	# "MANU_SC_1967_0029":"The Constitution (Forty-Fourth Amendment) Act 1978 and The Constitution (Forty-Fifth Amendment) Act 2002",
"MANU_SC_1975_0304":"Kesavananda Bharati v. State of Kerala",
"MANU_SC_1978_0133":"Passport Authority v. Government of India",
"MANU_SC_1983_0382":"State of Maharashtra vs. The Director General of Police and others",
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
import re

space_handler = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
def run_groq_model(messages, model, temperature=0.7, top_p=1, max_tokens=16):
	client = Groq(api_key=settings.GROQ_API_KEY)
	chat_completion = client.chat.completions.create(
		messages=messages, temperature=temperature, top_p=top_p,
		model=model, n=1, max_tokens=max_tokens
	)
	return chat_completion.choices[0].message.content
def processChunks(full_text,model_num,test):
	## Load full_text i.e. the text to be summarized
	full_text=space_handler(full_text)
	nlp.max_length = len(full_text) + 10000
	sentences = [sent.text for sent in nlp(full_text).sents]
	doc_chunk_len = 996
	chunks = create_chunks(sentences, doc_chunk_len)
	ret=""

	for chunk in chunks:
		if test:
			instruction= "Please Summarize the following text"
			source = f"### Instruction: {instruction.strip()} \n\n### Text: \n{space_handler(chunk).strip()} \n\n### Summary: "
		else:
			instruction = f"Summarize the following Indian Legal judgment while highlighting key points such as the main arguments, quotations from the court, court decisions, and any significant legal precedents or statutes cited."
			source = f"### Instruction: {instruction.strip()} \n\n### Judgment: \n{space_handler(chunk).strip()} \n\n### Summary: "
		ret+=run_groq_model([{"role": "user", "content": source}], models[model_num], max_tokens=1024)
	ret=re.sub(r'\n+', '\n', ret)

	return ret
# bad=['MANU_SC_2000_0046','MANU_SC_1978_0139','MANU_SC_2003_0234','MANU_SC_1980_0075','MANU_SC_2014_0043','MANU_SC_2013_0687']
# cases=['MANU_SC_2002_0189', 'MANU_SC_1975_0304', 'MANU_SC_1997_0157', 'MANU_SC_2012_0311', 'MANU_SC_1985_0039', 'MANU_SC_1978_0139', 'MANU_SC_2003_0234', 'MANU_SC_2008_3096', 'MANU_SC_1993_0333', 'MANU_SC_1983_0382', 'MANU_SC_2015_0329', 'MANU_SC_2006_0399', 'MANU_SC_1980_0075', 'MANU_SC_1978_0133', 'MANU_SC_2014_0043', 'MANU_SC_2010_0325', 'MANU_SC_1995_0290', 'MANU_SC_1967_0029', 'MANU_SC_2013_0687', 'MANU_SC_1986_0716', 'MANU_SC_2002_1141', 'MANU_SC_1997_0261', 'MANU_SC_2011_0176', 'MANU_SC_2002_0394']
# for case in bad:
# 	if case in cases:
# 		cases.remove(case) 


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
	case_root=os.path.join(settings.MEDIA_ROOT, "files")
	case_lang_root=os.path.join(settings.MEDIA_ROOT, "data")
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


from django.http import FileResponse
from django.urls import reverse

def download_pdf_view(request, case, language):
	# Generate the PDF file
	pdf_filename = f"{case}_{language}.pdf"
	pdf_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_filename)

	if pdf_filename is None:
		return HttpResponse("Error generating PDF", status=500)

	# Create the file path
	pdf_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_filename)
	
	# Serve the file
	return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=pdf_filename)

def home(request):
	# global cases
	# context={"output":"","input":"","form_submitted":False,"language":"English","model":"Llama 3 8B","modelname":models["Llama 3 8B"]}
	casesdict={key:{"name":value,"date":key[8:12]} for key,value in sorted(cases.items())}
	case_ids=list(casesdict.keys())
	context={"output":"","input":"","form_submitted":False,"language":"English","selected_case":case_ids[0],"cases":casesdict}
	if request.method == 'POST':
		print(request.POST)
		print(request.FILES)
		test = request.GET.get('test', 'false')  # Default to 'false' if not provided
		test = True if test=='true' else False
		print("post received",test)
		case_num=request.POST["case"]
		lang=request.POST["language"]
		error=None
		if case_num in cases:
			filename = f"Summ_English.txt"
			case_root=os.path.join(settings.MEDIA_ROOT, "files")

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
					text+=section+"\n"+value+"\n\n"
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
			context={"success":True,"output":ret,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"selected_case":case_num,"cases":casesdict}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
		else:
			error="Invalid case selection"
			context={"success":False,"error":error,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":case_num,"cases":casesdict}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
	else:
		# submitted = request.GET.get('submitted',False)
		# context["form_submitted"]=submitted
		# print("submitted",submitted,context)
		
		return render(request, 'home-1.html',context=context)

def home1(request):
	context={"output":"","input":"","form_submitted":False,"language":"English","model":"Llama 3 8B","modelname":models["Llama 3 8B"]}
	# context={"output":"","input":"","form_submitted":False,"language":"English","selected_case":cases[0],"cases":cases}
	if request.method == 'POST':
		print(request.POST)
		print(request.FILES)
		test = request.GET.get('test', 'false')  # Default to 'false' if not provided
		test = True if test=='true' else False
		print("post received",test)
		model_num=request.POST["model"]
		error=None
		if model_num not in models.keys():
			error="Invalid model selection"
		uploaded_file = request.FILES.get('file_input',None)
		print(uploaded_file)
		input_text=request.POST.get("input_text",None)
		if len(input_text)==0 and uploaded_file is None:
			error="Input is empty"
		lang=request.POST.get("language","English")
		if uploaded_file is not None and error is None:
			fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "files"))
			filename = fs.save(uploaded_file.name.replace(" ","_"), uploaded_file)
			uploaded_file_url = fs.url(filename)
			file_path = fs.path(filename)


			#file size 5mb limit

			# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			print(uploaded_file_url,file_path)
			ret=""

			reader = PdfReader(file_path)
			input_data=""
			for page in reader.pages:
				input_data+=page.extract_text()+"\n"
				if len(input_data)>=MAX_TOKENS:
					break
			ret = processChunks(input_data,model_num,test)
			if lang != 'English':
				if lang in language_setting.keys():
					pass
					# ret=indicTranslate(ret,lang)
					# ret=""
				else:
					error="Language not found"
					context={"success":False,"error":error,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num,"modelname":models[model_num]}
					# return redirect('/?submitted=True')
					return render(request, 'home-1.html',context=context)
				


			context={"success":True,"output":ret,"form_submitted":True,"language":request.POST["language"],"model":model_num,"modelname":models[model_num]}
			# return redirect('/?submitted=True')
			reader.close()
			
			if fs.exists(file_path):
				print("deleting",file_path)
				fs.delete(file_path)
			return render(request, 'home-1.html',context=context)
		elif input_text is not None and input_text !="" and error is None:
			ret=""
			ret = processChunks(input_text,model_num,test)
			if lang != 'English':
				if lang in language_setting.keys():
					# ret=indicTranslate(ret,lang)
					pass
				else:
					error="Language not found"
					context={"success":False,"error":error,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num,"modelname":models[model_num]}
					# return redirect('/?submitted=True')
					return render(request, 'home-1.html',context=context)
				
			# ret = run_groq_model([{"role": "user", "content": request.POST.get("input_text")}], "llama3-8b-8192", max_tokens=100)
			context={"success":True,"output":ret,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num,"modelname":models[model_num]}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
		else:
			context={"success":False,"error":error,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num,"modelname":models[model_num]}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
	else:
		# submitted = request.GET.get('submitted',False)
		# context["form_submitted"]=submitted
		# print("submitted",submitted,context)
		
		return render(request, 'home-1.html',context=context)

	# print(ret)




	