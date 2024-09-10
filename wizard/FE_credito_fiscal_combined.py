import logging
import os  # Add this line to import the os module
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
from datetime import timedelta
from lxml import etree

_logger = logging.getLogger(__name__)

PATRON_CORREO = r"\w+([-+.]\w+)*@\w+([-.]\\w+)*\.\w+([-.]\\w+)"
PATRON_TELEFONO = r"\d{3}-\d{3}-\d{4}"
PATRON_RNC = r"[0-9]{11}|[0-9]{9}"
PATRON_NUMEROPEDIDOINTERNO = r"[0-9]{1,20}"
PATRON_MONTOIMPUESTO = r"[0-9]{1,16}(\.[0-9]{1,2})?"
PATRON_ITBIS = r"[0-9]{1,2}"
PATRON_TASAIMPUESTO = r"[0-9]{1,3}(.[0-9]{1,2})?"

class AccountFEDomCombined(models.TransientModel):
    _name = "account_fe.dom.combined"
    _inherit = "account_fe.dom"

    def generate_combined_xml(self):
        # Crear el elemento raíz del XML
        root = etree.Element("ComprobanteFiscalElectronico")

        # Llamar a los métodos heredados para generar las diferentes secciones
        encabezado = self.Creacion_encabezado()
        emisor = self.Creacion_emisor()
        comprador = self.Creacion_comprador()
        impuestos_adicionales = self.Creacion_impuestos_adicionales()
        otra_moneda = self.Creacion_otra_moneda_encabezado()

        # Añadir las secciones al XML
        root.append(self.dict_to_xml("Encabezado", encabezado))
        root.append(self.dict_to_xml("Emisor", emisor))
        root.append(self.dict_to_xml("Comprador", comprador))
        if impuestos_adicionales:
            root.append(self.dict_to_xml("ImpuestosAdicionales", impuestos_adicionales))
        if otra_moneda:
            root.append(self.dict_to_xml("OtraMoneda", otra_moneda))

        # Generar el XML como string
        xml_string = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        
        return xml_string

    def dict_to_xml(self, tag, d):
        elem = etree.Element(tag)
        for key, val in d.items():
            child = etree.Element(key)
            if isinstance(val, dict):
                child = self.dict_to_xml(key, val)
            else:
                child.text = str(val)
            elem.append(child)
        return elem



    def verify_xml(self, xml_string, xsd_files):
        for xsd_file in xsd_files:
            try:
                xmlschema_doc = etree.parse(xsd_file)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                xml_doc = etree.fromstring(xml_string)
                xmlschema.assert_(xml_doc)
                return True, f"XML válido según el esquema {os.path.basename(xsd_file)}."
            except etree.DocumentInvalid as err:
                _logger.warning(f"Validación fallida para {os.path.basename(xsd_file)}: {err}")
            except Exception as e:
                _logger.error(f"Error al procesar {os.path.basename(xsd_file)}: {e}")
        
        return False, "XML inválido: No cumple con ninguno de los esquemas XSD proporcionados."


    def action_generate_and_verify_xml(self):
        xml_string = self.generate_combined_xml()
        
        # Directorio base de los archivos XSD
        xsd_base_path = "../egestion_account_FE_dom/static/src/xml"
        
        # Seleccionar los archivos XSD apropiados basados en el tipo de comprobante
        xsd_files = []
        if self.TipoeCF in ['31', '32', '33', '34', '41', '43', '44', '45', '46', '47']:
            xsd_files.append(os.path.join(xsd_base_path, f"e-CF {self.TipoeCF} v.1.0.xsd"))
        
        # Añadir otros archivos XSD relevantes
        additional_xsds = ["ACECF v.1.0.xsd", "ANECF v.1.0.xsd", "ARECF v1.0.xsd", "Semilla v.1.0.xsd"]
        xsd_files.extend([os.path.join(xsd_base_path, xsd) for xsd in additional_xsds])
        
        # Si es una factura de consumo (tipo 32), añadir el XSD específico
        if self.TipoeCF == '32':
            xsd_files.append(os.path.join(xsd_base_path, "RFCE 32 v.1.0.xsd"))
        
        is_valid, message = self.verify_xml(xml_string, xsd_files)
        
        if is_valid:
            # Aquí puedes guardar el XML, enviarlo a algún lado, etc.
            _logger.info("XML generado y validado correctamente")
        else:
            raise ValidationError(message)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Resultado de la generación de XML'),
                'message': message,
                'type': 'success' if is_valid else 'warning',
                'sticky': False,
            }
        }