from django.shortcuts import render,redirect
from groq import Groq
from legal_text import settings
from django.core.files.storage import FileSystemStorage
from pypdf import PdfReader
MAX_TOKENS=500
import os
models={
	1:"llama3-8b-8192",
	2:"mixtral-8x7b-32768"
}
def run_groq_model(messages, model, temperature=0.7, top_p=1, max_tokens=16):
	client = Groq(api_key=settings.GROQ_API_KEY)
	chat_completion = client.chat.completions.create(
		messages=messages, temperature=temperature, top_p=top_p,
		model=model, n=1, max_tokens=max_tokens
	)
	return chat_completion.choices[0].message.content
def home(request):
	context={"output":"Output appears here","input":"","form_submitted":False,"language":"English","model":1}
	if request.method == 'POST':
		print(request.POST)
		print(request.FILES)
		model_num=int(request.POST["model"])
		error=None
		if model_num>len(models.keys()):
			error="Invalid model selection"
		uploaded_file = request.FILES.get('file_input',None)
		print(uploaded_file)
		input_text=request.POST.get("input_text",None)
		if len(input_text)==0 and uploaded_file is None:
			error="Input is empty"

		if uploaded_file is not None and error is None:
			fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "files"))
			filename = fs.save(uploaded_file.name.replace(" ","_"), uploaded_file)
			uploaded_file_url = fs.url(filename)
			file_path = fs.path(filename)

			# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			print(uploaded_file_url,file_path)
			ret="first"

			reader = PdfReader(file_path)
			input_data=""
			for page in reader.pages:
				input_data+=page.extract_text()+"\n"
				if len(input_data)>=MAX_TOKENS:
					break
			ret = run_groq_model([{"role": "user", "content": input_data}], models[model_num], max_tokens=500)
			context={"success":True,"output":ret,"form_submitted":True,"language":request.POST["language"],"model":model_num}
			# return redirect('/?submitted=True')
			reader.close()
			
			if fs.exists(file_path):
				print("deleting",file_path)
				fs.delete(file_path)
			return render(request, 'home-1.html',context=context)
		elif input_text is not None and input_text !="" and error is None:
			ret="second"
			ret = run_groq_model([{"role": "user", "content": request.POST.get("input_text")}], "llama3-8b-8192", max_tokens=100)
			context={"success":True,"output":ret,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
		else:
			context={"success":False,"error":error,"input":request.POST.get("input_text"),"form_submitted":True,"language":request.POST["language"],"model":model_num}
			# return redirect('/?submitted=True')
			return render(request, 'home-1.html',context=context)
	else:
		# submitted = request.GET.get('submitted',False)
		# context["form_submitted"]=submitted
		# print("submitted",submitted,context)
		return render(request, 'home-1.html',context=context)

	# print(ret)