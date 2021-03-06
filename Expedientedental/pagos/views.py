# encoding:utf-8
from datetime import datetime
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView

from wkhtmltopdf.views import PDFTemplateView

from core.utils import generic_search, paginate_objects
from core.mixins import PermissionRequiredMixin

from altas.models import Paciente
from cotizacion.models import Cotizacion
from servicios.models import PaqueteServicios, Servicio
from pagos.models import Pago, PagoAplicado
from pagos.forms import PagoForm, PagoAplicadoFormset


@permission_required('pagos.add_pagoaplicado')
def pagos(request, paquete_id):

    paquete = get_object_or_404(PaqueteServicios, pk=paquete_id)
    total = paquete.total()
    servicios = paquete.servicio_set.filter(status__in=['aceptado', 'parcial'])
    paciente = paquete.odontograma.paciente
    initial = []

    for servicio in servicios:
        initial.append({
            'importe': 0,
            'servicio': servicio
            })

    pa_formset = None

    if request.method == "POST":
        modelform = PagoForm(request.POST)
        pa_formset = PagoAplicadoFormset(request.POST, initial=initial)

        if modelform.is_valid():
            pago = modelform.save(commit=False)
            if pa_formset.is_valid(pago.monto):
                pago.save()

                monto_aplicado = 0
                for form in pa_formset:
                    form.instance.importe
                    pago_aplicado = form.save(pago)
                    monto_aplicado += pago_aplicado.importe

                    if pago_aplicado.importe > 0:
                        servicio = pago_aplicado.servicio
                        pagoaplicado_set = servicio.pagoaplicado_set
                        total_aplicado = pagoaplicado_set.total_pagado()

                        if total_aplicado == servicio.precio:
                            servicio.status = 'pagado'

                            servicio.procedimiento.status = 'autorizado'
                            servicio.procedimiento.save()

                        else:
                            servicio.status = 'parcial'

                        servicio.save()

                pago.aplicamonto(monto_aplicado)
                pago.save()

                return redirect(reverse('pagos:pagos_detail', args=[pago.id]))
    else:
        modelform = PagoForm(initial={
                             'monto': paquete.total_adeudado(),
                             'paciente': paciente
                             })
        pa_formset = PagoAplicadoFormset(initial=initial)

    servicios = [form.servicio for form in pa_formset]

    return render(request, 'pago.html', {
                  'form': modelform,
                  'pa_formset': pa_formset,
                  'servicios': servicios,
                  'total': total,
                  'paquete': paquete,
                  'rp_active': 'active'
                  })


@permission_required('pagos.add_pago')
def pagos_list(request):
    ''' Todos los pagos realizados. '''
    pagos = Pago.objects.order_by('-fecha')
    query = 'q'

    MODEL_MAP = {
        Paciente: [
            'nombre',
            'apellidoPaterno',
            'apellidoMaterno',
            'credencialPaciente'
        ],
    }

    objects = []

    for model, fields in MODEL_MAP.iteritems():
        objects += generic_search(request, model, fields, query)

    paginator, page_obj, object_list, is_paginated = paginate_objects(
        request, objects, 20)

    return render(request, 'pago-list.html', {
        'pagos': pagos,
        'objects': object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': is_paginated,
        'search_string': request.GET.get(query, ''),
        'r_active': 'active'
        })


@permission_required('pagos.add_pago')
def paciente_search(request):
    '''
    Lista de pacientes con pagos pendientes.
    '''
    query = 'q'

    MODEL_MAP = {
        Paciente: [
            'nombre',
            'apellidoPaterno',
            'apellidoMaterno',
            'credencialPaciente'
        ],
    }

    objects = []

    for model, fields in MODEL_MAP.iteritems():
        objects += generic_search(request, model, fields, query)

    paginator, page_obj, object_list, is_paginated = paginate_objects(
        request, objects, 20)

    return render(request, 'pago-paciente-search.html', {
        'objects': object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': is_paginated,
        'search_string': request.GET.get(query, ''),
        'rp_active': 'active'
        })


class PagosPacienteList(PermissionRequiredMixin, DetailView):
    ''' Pagos realizados por paciente. '''
    model = Paciente
    context_object_name = 'paciente'
    template_name = 'pago-paciente.html'
    permission_required = 'pagos.add_pago'

    def get_context_data(self, **kwargs):
        context = super(PagosPacienteList, self).get_context_data(**kwargs)
        pagos = self.object.pago_set.all()
        context.update({'r_active': 'active', 'pagos': pagos})
        return context


class PagosCotizacionList(PermissionRequiredMixin, DetailView):
    ''' Pagos realizados a una cotizacion. '''
    model = Cotizacion
    context_object_name = 'cotizacion'
    template_name = 'pago-cotizacion.html'
    permission_required = 'pagos.add_pago'

    def get_context_data(self, **kwargs):
        context = super(PagosCotizacionList, self).get_context_data(**kwargs)
        paciente = self.object.odontograma.paciente
        pagos = PagoAplicado.objects.filter(
            pago__paciente=paciente)
        context.update({
            'pagos': pagos,
            'paciente': paciente,
            'r_active': 'active'})
        return context


class PagosServicio(PermissionRequiredMixin, DetailView):
    ''' Pagos por servicio. '''
    model = Servicio
    context_object_name = 'servicio'
    template_name = 'pago-servicio.html'
    permission_required = 'pagos.add_pago'

    def get_context_data(self, **kwargs):
        context = super(PagosServicio, self).get_context_data(**kwargs)
        pagos = self.object.pagoaplicado_set.all()
        paciente = self.object.pago_set.all()[0].paciente
        context.update({
            'pagos': pagos,
            'paciente': paciente,
            'r_active': 'active'})
        return context


class PagosServicios(PermissionRequiredMixin, DetailView):
    ''' Lista de servicios con pagos. '''
    model = Paciente
    context_object_name = 'paciente'
    template_name = 'pago-servicios.html'
    permission_required = 'pagos.add_pago'

    def get_context_data(self, **kwargs):
        context = super(PagosServicios, self).get_context_data(**kwargs)
        servicios = Servicio.objects.all()
        context.update({'servicios': servicios, 'r_active': 'active'})
        return context


class PagosPending(PermissionRequiredMixin, DetailView):
    '''
    Lista de pagos pendientes agrupados por cotizacion.
    '''
    model = Paciente
    context_object_name = 'paciente'
    template_name = 'pago-pending.html'
    permission_required = 'pagos.add_pagoaplicado'

    def get_context_data(self, **kwargs):
        context = super(PagosPending, self).get_context_data(**kwargs)
        paquetes = PaqueteServicios.objects.filter(
            odontograma__paciente=self.object)
        # Quitamos paquetes que no tengan items que cobrar (total = 0)
        paquetes = [
            p for p in paquetes if p.total() != 0 and p.total_adeudado() != 0
        ]
        context.update({'rp_active': 'active', 'paquetes': paquetes})
        return context


class PagosDetail(PermissionRequiredMixin, DetailView):
    model = Pago
    show_content_in_browser = True
    context_object_name = 'pago'
    template_name = 'pago-detail.html'
    footer_template = 'footerpdf.html'
    permission_required = 'pagos.add_pago'
    cmd_options = {
        'margin-top': 15,
        'margin-bottom': 20,
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(PagosDetail, self).get_context_data(**kwargs)
        paciente = self.object.paciente
        context.update({'r_active': 'active', 'paciente': paciente})
        return context


class RecibodePagoPDF(PDFTemplateView):
    '''
    recibo que se le entrega al paciente cada vez
    que hace un pago o un abono.
    '''

    filename = 'recibo.pdf'
    show_content_in_browser = True
    template_name = 'recibo_pago.html'
    footer_template = 'footerpdf.html'
    medico = None

    cmd_options = {
        'margin-top': 10,
        'margin-bottom': 20,
        'page-size': 'Letter'
    }

    def get_medico(self):
        if self.medico is None:
            servicio = self.pago.servicios.all()[0]
            self.medico = servicio.procedimiento.odontograma.medico
        return self.medico

    def get_context_data(self, **kwargs):
        context = super(RecibodePagoPDF, self).get_context_data(**kwargs)
        self.pago_id = int(kwargs.get('pago_id'))
        pago = get_object_or_404(Pago, pk=self.pago_id)
        self.pago = pago
        medico = self.get_medico()
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'medico': medico,
            'pago': pago,
            'fecha': fecha,
            'hora': hora,
            'low_margin': 'low-margin'
            })
        return context


class HistorialPagosPDF(PDFTemplateView):

    '''
    pdf que hace posible entrgar un estado de cuenta del paciente
    '''
    filename = 'recibo_de_entrega.pdf'
    show_content_in_browser = True
    template_name = 'historial_pagos.html'
    footer_template = 'footerpdf.html'
    paciente = None
    cmd_options = {
        'margin-top': 20,
        'margin-bottom': 20,
        'page-size': 'Letter'
    }

    def get_paciente(self):
        if self.paciente is None:
            servicio = self.pagos[0].servicio
            self.paciente = servicio.procedimiento.odontograma.paciente
        return self.paciente

    def get_context_data(self, **kwargs):
        context = super(HistorialPagosPDF, self).get_context_data(**kwargs)
        self.pagos = PagoAplicado.objects.all()
        paciente = self.get_paciente
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'paciente': paciente,
            'pagos': self.pagos,
            'fecha': fecha, 'hora': hora
        })
        return context
