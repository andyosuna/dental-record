from datetime import datetime
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from wkhtmltopdf.views import PDFTemplateView
from core.mixins import PermissionRequiredMixin

from cotizacion.models import Cotizacion
from cotizacion.forms import ItemFormSet


class CotizacionList(PermissionRequiredMixin, ListView):
    model = Cotizacion
    context_object_name = 'cotizaciones'
    template_name = 'cotizaciones.html'
    permission_required = 'cotizacion.add_cotizacion'
    paginate_by = 20

    def get_queryset(self):
        cotizaciones_pk = []
        for c in self.model.objects.all():
            if c.total() == c.total_procesado():
                cotizaciones_pk.append(c.pk)
        cotizaciones = self.model.objects.exclude(pk__in=cotizaciones_pk)
        return cotizaciones

    def get_context_data(self, **kwargs):
        context = super(CotizacionList, self).get_context_data(**kwargs)
        context.update({'c_active': 'active'})
        return context


class ProcesadoList(PermissionRequiredMixin, ListView):
    model = Cotizacion
    context_object_name = 'orders'
    template_name = 'cotizaciones-procesadas.html'
    permission_required = 'cotizacion.add_cotizacion'
    paginate_by = 20

    def get_queryset(self):
        cotizaciones_pk = []
        for c in self.model.objects.all():
            if c.total() == c.total_procesado():
                cotizaciones_pk.append(c.pk)
        cotizaciones = self.model.objects.filter(pk__in=cotizaciones_pk)
        return cotizaciones

    def get_context_data(self, **kwargs):
        context = super(ProcesadoList, self).get_context_data(**kwargs)
        context.update({'cp_active': 'active'})
        return context


@permission_required('cotizacion.add_cotizacion')
def cotizacion_detail(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    items = cotizacion.cotizacionitem_set.all()

    if request.method == 'POST':
        formset = ItemFormSet(request.POST)

        if formset.is_valid():
            formset.save()

    else:
        formset = ItemFormSet(queryset=items)

    total = cotizacion.total_aceptado()
    paciente = cotizacion.odontograma.paciente

    return render(request, 'cotizacion.html', {
                  'cotizacion': cotizacion,
                  'paciente': paciente,
                  'items': items,
                  'formset': formset,
                  'total': total,
                  'c_active': 'active'})


class CotizacionPDF(PDFTemplateView):
    '''
    view pdf que contiene datos de la cotizacion y sus items
    '''
    filename = 'cotizacion.pdf'
    show_content_in_browser = True
    template_name = 'printit.html'
    footer_template = 'footerpdf.html'
    cmd_options = {
        'margin-top': 20,
        'margin-bottom': 20,
        'page-size': 'Letter'
    }

    def get_context_data(self, **kwargs):
        context = super(CotizacionPDF, self).get_context_data(**kwargs)
        cotizacion = Cotizacion.objects.get(pk=self.kwargs.get('pk'))
        items = cotizacion.cotizacionitem_set.all()
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'cotizacion': cotizacion, 'items': items,
            'fecha': fecha, 'hora': hora
        })
        return context
