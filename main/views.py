from django.shortcuts import render,redirect
from groq import Groq
from legal_text import settings
from django.core.files.storage import FileSystemStorage
from pypdf import PdfReader
import os
MAX_TOKENS=500
from nltk.tokenize import word_tokenize,sent_tokenize
from .indicTrans import initialize_model_and_tokenizer, batch_translate
from .cleanJudgement import clean_judgment
quantization = None
model_id = "ai4bharat/indictrans2-en-indic-1B"  # ai4bharat/indictrans2-en-indic-dist-200M
en_indic_ckpt_dir=settings.MODEL_DIR
en_indic_tokenizer, en_indic_model = initialize_model_and_tokenizer(model_id,en_indic_ckpt_dir, "en-indic", quantization)
language_setting={
	"Hindi":"hin_Deva",
	"Bengali":"ben_Beng",
}

def split_text_into_sentences(text):
    sentences = sent_tokenize(text)
    return sentences

def indicTranslate(in_text,out_lang):
	src_lang, tgt_lang = "eng_Latn", language_setting[out_lang]
	en_sents=split_text_into_sentences(in_text)
	print(en_sents)
	hi_translations = batch_translate(en_sents, src_lang, tgt_lang, en_indic_model, en_indic_tokenizer)
	print(f"\n{src_lang} - {tgt_lang}")
	ret=""
	for input_sentence, translation in zip(en_sents, hi_translations):
		print(f"{src_lang}: {input_sentence}")
		print(f"{tgt_lang}: {translation}")
		ret+=translation+" "
	return ret




def count_tkn_with_tokenizer(txt: str) -> int:
    return len(word_tokenize(txt))
# Load the tokenizer

import spacy
# !python -m spacy download en_core_web_lg --quiet
nlp = spacy.load("en_core_web_lg")


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
	return ret


def home(request):
	context={"output":"","input":"","form_submitted":False,"language":"English","model":"Llama 3 8B","modelname":models["Llama 3 8B"]}
	if request.method == 'POST':
		print(request.POST)
		print(request.FILES)
		test = bool(request.GET.get('test',False))
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
					ret=indicTranslate(ret,lang)
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
					ret=indicTranslate(ret,lang)
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