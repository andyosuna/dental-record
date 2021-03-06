# encoding:utf-8
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render
from django.views.generic import ListView, UpdateView, CreateView, DetailView

from wkhtmltopdf.views import PDFTemplateView
from core.utils import generic_search, paginate_objects
from core.mixins import PermissionRequiredMixin
from core.views import CreateObjFromContext

from inventario.models import (
    UnidadMedida, Producto, Entrada, CancelEntrada, CancelProducto
)
from inventario.forms import (
    ProductoForm, UnidadMedidaForm, EntradaForm, EntradaCanceladaForm,
    CancelEntradaForm, ProductoUpdateForm, ProductoCancelForm,
    CancelProductoForm
)


@permission_required('inventario.add_producto')
def busqueda(request):
    query = 'q'
    MODEL_MAP = {
        Producto: ['nombre', 'porciones'],
    }

    objects = []

    for model, fields in MODEL_MAP.iteritems():
        objects += generic_search(request, model, fields, query)

    paginator, page_obj, object_list, is_paginated = paginate_objects(
        request, objects, 20)

    return render(request, 'producto-search.html', {
        'objects': object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': is_paginated,
        'search_string': request.GET.get(query, ''),
        's_active': 'active'
        })


class Productos(PermissionRequiredMixin, ListView):
    model = Producto
    queryset = model.objects.filter(is_inactive=False)
    context_object_name = 'productos'
    template_name = 'productos.html'
    permission_required = 'inventario.add_producto'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(Productos, self).get_context_data(**kwargs)
        context.update({'i_active': 'active'})
        return context


class ProductoCreate(PermissionRequiredMixin, CreateView):
    form_class = ProductoForm
    template_name = 'producto.html'
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = 'inventario.add_producto'

    def get_context_data(self, **kwargs):
        context = super(ProductoCreate, self).get_context_data(**kwargs)
        context.update({'pc_active': 'active'})
        return context


class ProductoUpdate(PermissionRequiredMixin, UpdateView):
    form_class = ProductoUpdateForm
    model = Producto
    template_name = 'producto.html'
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = 'inventario.change_producto'

    def get_context_data(self, **kwargs):
        context = super(ProductoUpdate, self).get_context_data(**kwargs)
        context.update({'i_active': 'active'})
        return context


class ProductoDetail(PermissionRequiredMixin, UpdateView):
    form_class = ProductoCancelForm
    model = Producto
    template_name = 'producto-detail.html'
    permission_required = 'inventario.add_producto'

    def get_context_data(self, **kwargs):
        context = super(ProductoDetail, self).get_context_data(**kwargs)
        context.update({'i_active': 'active'})
        return context

    def get_success_url(self):
        url = reverse('inventario:producto_cancel', kwargs=self.kwargs)
        return url


class ProductoCancel(PermissionRequiredMixin, CreateObjFromContext):
    form_class = CancelProductoForm
    ctx_model = Producto
    template_name = 'producto-cancel.html'
    success_url = reverse_lazy('inventario:productos_cancelados')
    permission_required = 'inventario.add_cancelproducto'
    initial_value = 'producto'

    def get_context_data(self, **kwargs):
        context = super(ProductoCancel, self).get_context_data(**kwargs)
        context.update({'pde_active': 'active'})
        return context


class ProductosCancelled(PermissionRequiredMixin, ListView):
    model = Producto
    queryset = model.objects.filter(is_inactive=True)
    context_object_name = 'productos'
    template_name = 'productos-cancelados.html'
    permission_required = 'inventario.add_cancelproducto'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ProductosCancelled, self).get_context_data(**kwargs)
        context.update({'pde_active': 'active'})
        return context


class ProductoCancelDetail(PermissionRequiredMixin, DetailView):
    model = CancelProducto
    context_object_name = 'cancelproducto'
    template_name = 'producto-cancel-detail.html'
    permission_required = 'inventario.add_cancelproducto'

    def get_context_data(self, **kwargs):
        context = super(ProductoCancelDetail, self).get_context_data(**kwargs)
        context.update({
            'producto': self.object.producto,
            'pde_active': 'active'
            })
        return context


class Unidades(PermissionRequiredMixin, ListView):
    model = UnidadMedida
    context_object_name = 'unidades'
    template_name = 'unidades.html'
    permission_required = 'inventario.add_unidadmedida'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(Unidades, self).get_context_data(**kwargs)
        context.update({'u_active': 'active'})
        return context


class UnidadCreate(PermissionRequiredMixin, CreateView):
    form_class = UnidadMedidaForm
    model = UnidadMedida
    template_name = 'unidad.html'
    success_url = reverse_lazy('inventario:unidades')
    permission_required = 'inventario.add_unidadmedida'

    def get_context_data(self, **kwargs):
        context = super(UnidadCreate, self).get_context_data(**kwargs)
        context.update({'u_active': 'active'})
        return context


class EntradaList(PermissionRequiredMixin, ListView):
    model = Entrada
    queryset = model.objects.filter(is_cancelled=False)
    context_object_name = 'entradas'
    template_name = 'entradas.html'
    permission_required = 'inventario.add_entrada'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EntradaList, self).get_context_data(**kwargs)
        context.update({'e_active': 'active'})
        return context


class EntradaDetail(PermissionRequiredMixin, UpdateView):
    form_class = EntradaCanceladaForm
    model = Entrada
    context_object_name = 'entrada'
    template_name = 'entrada-detail.html'
    permission_required = 'inventario.change_entrada'

    def get_context_data(self, **kwargs):
        context = super(EntradaDetail, self).get_context_data(**kwargs)
        context.update({'e_active': 'active'})
        return context

    def get_success_url(self):
        url = reverse('inventario:entrada_cancel', kwargs=self.kwargs)
        return url


class EntradaProducto(PermissionRequiredMixin, CreateObjFromContext):
    form_class = EntradaForm
    template_name = 'entrada.html'
    ctx_model = Producto
    initial_value = 'producto'
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = 'inventario.change_producto'

    def get_context_data(self, **kwargs):
        context = super(EntradaProducto, self).get_context_data(**kwargs)
        context.update({'i_active': 'active'})
        return context

    def form_valid(self, form):
        producto = self.get_obj()
        porciones = int(form.cleaned_data.get('porciones'))
        producto.agregar(porciones)
        producto.save()
        return super(EntradaProducto, self).form_valid(form)


class EntradasCancelledList(PermissionRequiredMixin, ListView):
    model = Entrada
    queryset = model.objects.filter(is_cancelled=True)
    context_object_name = 'entradas'
    template_name = 'entradas-canceladas.html'
    permission_required = 'inventario.add_cancelentrada'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EntradasCancelledList, self).get_context_data(**kwargs)
        cancelled = CancelEntrada.objects.all()
        context.update({'cancelentrada': cancelled, 'ec_active': 'active'})
        return context


class EntradaCancel(PermissionRequiredMixin, CreateObjFromContext):
    form_class = CancelEntradaForm
    ctx_model = Entrada
    template_name = 'entrada-cancel.html'
    success_url = reverse_lazy('inventario:entradas_canceladas')
    permission_required = 'inventario.add_cancelentrada'
    initial_value = 'entrada'

    def get_context_data(self, **kwargs):
        context = super(EntradaCancel, self).get_context_data(**kwargs)
        context.update({'e_active': 'active'})
        return context


class EntradaCancelDetail(PermissionRequiredMixin, DetailView):
    model = CancelEntrada
    template_name = 'entradacancel-detail.html'
    permission_required = 'inventario.add_cancelentrada'
    context_object_name = 'cancelentrada'

    def get_context_data(self, **kwargs):
        context = super(EntradaCancelDetail, self).get_context_data(**kwargs)
        entrada = self.object.entrada
        context.update({'entrada': entrada, 'ec_active': 'active'})
        return context


class ProductosPDF(PDFTemplateView):
    '''
    pdf de lista de productos muesra su status asi como
    las existencias dentro del inventario:lista de productos
    '''
    filename = 'productos.pdf'
    show_content_in_browser = True
    template_name = 'productos-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(ProductosPDF, self).get_context_data(**kwargs)
        productos = Producto.objects.order_by('-updated_at')
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({'productos': productos, 'fecha': fecha, 'hora': hora})
        return context


class ProductoPdf(PDFTemplateView):
    '''
    view dedicada a imprimir el detalle de un prducto
    inventario:detalle de prodcuto
    '''

    filename = 'producto.pdf'
    show_content_in_browser = True
    template_name = 'producto-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(ProductoPdf, self).get_context_data(**kwargs)
        producto = Producto.objects.get(pk=self.kwargs.get('pk'))
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({'producto': producto, 'fecha': fecha, 'hora': hora})
        return context


class ProductoCanceladoPDF(PDFTemplateView):
    '''
    pdf de producto desactivado muestra el detalle
    de desactivacion asi como los detalles del producto
    '''
    filename = 'producto-cancelado.pdf'
    show_content_in_browser = True
    template_name = 'producto-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(ProductoCanceladoPDF, self).get_context_data(**kwargs)
        producto = Producto.objects.get(pk=self.kwargs.get('pk'))
        cancelproducto = producto.cancelproducto_set.get()
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'producto': producto, 'cancelproducto': cancelproducto,
            'fecha': fecha, 'hora': hora})
        return context


class EntradasPDF(PDFTemplateView):
    '''
    pdf muestra el detalle de la entradas del isnumo
    a inventario lista de las entradas
    '''

    filename = 'entradas.pdf'
    show_content_in_browser = True
    template_name = 'entradas-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(EntradasPDF, self).get_context_data(**kwargs)
        entradas = Entrada.objects.filter(
            is_cancelled=False).order_by('-updated_at')
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({'entradas': entradas, 'fecha': fecha, 'hora': hora})
        return context


class EntradaPDF(PDFTemplateView):
    '''
    pdf que muetra la entrada del producto ,detalle
    asi como existencias
    '''
    filename = 'entrada.pdf'
    show_content_in_browser = True
    template_name = 'entrada-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(EntradaPDF, self).get_context_data(**kwargs)
        entrada = Entrada.objects.get(pk=self.kwargs.get('pk'))
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({'entrada': entrada, 'fecha': fecha, 'hora': hora})
        return context


class EntradasCanceladasPDF(PDFTemplateView):
    '''
    pdf que muestra todas las entradas-canceladas
    lista
    '''
    filename = 'entradas-canceladas.pdf'
    show_content_in_browser = True
    template_name = 'entradas-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': '20',
        'margin-bottom': '20',
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(EntradasCanceladasPDF, self).get_context_data(**kwargs)
        entradas = Entrada.objects.filter(
            is_cancelled=True).order_by('-updated_at')
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'entradas': entradas, 'fecha': fecha, 'hora': hora, 'c': 'c'
        })
        return context


class EntradaCanceladaPDF(PDFTemplateView):
    '''
    pdf de entradas canceladas detalle de la cancelacion
    '''
    filename = 'entrada-cancelada.pdf'
    show_content_in_browser = True
    template_name = 'entrada-pdf.html'
    footer_template = 'footerpdf.html'

    cmd_options = {
        'margin-top': 20,
        'margin-bottom': 20,
        'page-size': 'Letter',
    }

    def get_context_data(self, **kwargs):
        context = super(EntradaCanceladaPDF, self).get_context_data(**kwargs)
        cancelentrada = CancelEntrada.objects.get(pk=self.kwargs.get('pk'))
        entrada = cancelentrada.entrada
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        context.update({
            'cancelentrada': cancelentrada, 'entrada': entrada,
            'fecha': fecha, 'hora': hora
        })
        return context
