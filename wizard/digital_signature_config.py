from odoo import models, fields, api

class DigitalSignatureConfig(models.Model):
    _name = 'digital.signature.config'
    _description = 'Configuración de Firma Digital'

    name = fields.Char('Nombre', required=True)
    p12_file = fields.Binary('Archivo P12', required=True)
    p12_password = fields.Char('Contraseña P12', required=True)

    @api.model
    def get_active_config(self):
        return self.search([], limit=1)