from django.db import models

# Create your models here.
'''
# Modelo de Notas Agregadas

class notas(models.Model):
	descripcion	= models.TextField()
	fechayHora = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		Nota = "%s %s"%(self.Descripcion,self.fechayHora)
		return Nota


# Modelo de Bitacora de Procedimientos

class bitacora(models.Model):
	nombredelProcedimiento = models.CharField(max_length=70)
	fechayhora = models.DateTimeField(blank=True, null=True)
	numerodeNota = models.ForeignKey(notas)

	def __unicode__(self):
<<<<<<< HEAD
		DatosBitacora = "%s %s"%(self.numero_de_nota,self.Nombre_del_Procedimiento,self.Fecha_y_Hora)
		return DatosBitacora
		'''
=======
		datosBitacora = "%s %s"%(self.numero_de_nota,self.Nombre_del_Procedimiento,self.Fecha_y_Hora)
		return DatosBitacora
>>>>>>> eb6ad5b6e2f16f8d923d4958e25b7f5ad0bd7a2f