#encoding:utf-8
from django.template.loader import get_template
from django.template import RequestContext
from django.http import Http404, HttpResponse
from .forms import OdontogramaForm, HistoriaClinicaForm, ListadeDiagnosticosForm
from .forms import ListadeDiagnosticosForm
from django.shortcuts import render_to_response, render, redirect
import datetime
from ActividadesClinicas.models import HistoriaClinica, Odontograma, ListadeDiagnosticos
#from ActividadesClinicas.models import ListadeDiagnosticos
from django.db.models import Q

def interrogatorio(request):
	if request.method == "POST":
		modelform = HistoriaClinicaForm(request.POST)
		if modelform.is_valid():
			modelform.save()
			return redirect("/interrogatorio/")
	else:
		modelform=HistoriaClinicaForm()
	return render(request,"interrogatorio.html",{"form":modelform})

def odontograma(request):
    query = request.GET.get('q', '')
    if query:
        qset = (
            Q(paciente__nombre__exact=query)
        )
        results = Odontograma.objects.filter(qset).distinct()
    else:
        results = []    
    consulta = Odontograma.objects.all()
    if request.method == "POST":
        modelform = OdontogramaForm(request.POST)
        if modelform.is_valid():
            modelform.save()
            return redirect("/odontograma/")
    else:
        modelform = OdontogramaForm()
    return render(request, "odontograma.html", {"form": modelform,'datospaciente': consulta[0:],"results": results,
        "query": query})


def diagnosticos(request):
    if request.method == "POST":
        modelform = ListadeDiagnosticosForm(request.POST)
        if modelform.is_valid():
            modelform.save()
            return redirect("/diagnosticos/")
    else:
        modelform = ListadeDiagnosticosForm()
    return render(request, "diagnosticos.html", {"form": modelform})

def datospaciente(request):
    consulta = Odontograma.objects.all()
    return render(request, 'prueba.html', {'datospaciente': consulta[0:]})

