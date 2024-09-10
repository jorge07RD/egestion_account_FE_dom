import base64
from odoo import http
from odoo.http import request
import requests
from lxml import etree
from signxml import XMLSigner
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

class ECFController(http.Controller):

    @http.route('/ecf/generate_xml', type='json', auth='user')
    def generate_xml(self, **kwargs):
        # Aquí llamarías a tu método para generar el XML
        account_fe = request.env['account_fe.dom.combined'].create({})
        xml_string = account_fe.generate_combined_xml()
        return {'xml': xml_string}

    @http.route('/ecf/sign_xml', type='json', auth='user')
    def sign_xml(self, xml_string, **kwargs):
        config = request.env['digital.signature.config'].get_active_config()
        if not config:
            return {'error': 'No se encontró configuración de firma digital'}

        p12_data = base64.b64decode(config.p12_file)
        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            p12_data, config.p12_password.encode(), backend=default_backend()
        )
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

        root = etree.fromstring(xml_string)
        signer = XMLSigner(
            method=signxml.methods.enveloped,
            signature_algorithm="rsa-sha256",
            digest_algorithm="sha256",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
        )
        signed_root = signer.sign(root, key=private_key, cert=cert_pem)
        signed_xml = etree.tostring(signed_root, encoding='unicode', pretty_print=False)

        return {'signed_xml': signed_xml}

    @http.route('/ecf/get_semilla', type='json', auth='user')
    def get_semilla(self, **kwargs):
        URL = "https://ecf.dgii.gov.do/certecf/autenticacion/api/Autenticacion/Semilla"
        headers = {
            "accept": "application/json",
            "Cookie": "NSC_ESNS=13170ea7-7283-1685-9678-2a87ba30e088_1225887533_0746960124_00000000004614803573",
        }
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            return {'semilla': response.text.split("\n", 1)[1]}
        else:
            return {'error': f'Error al obtener semilla: {response.status_code}'}

    @http.route('/ecf/process_document', type='json', auth='user')
    def process_document(self, **kwargs):
        # 1. Generar XML
        xml_result = self.generate_xml()
        if 'error' in xml_result:
            return xml_result

        # 2. Firmar XML
        sign_result = self.sign_xml(xml_result['xml'])
        if 'error' in sign_result:
            return sign_result

        # 3. Obtener semilla
        semilla_result = self.get_semilla()
        if 'error' in semilla_result:
            return semilla_result

        # 4. Firmar semilla
        signed_semilla = self.sign_xml(semilla_result['semilla'])
        if 'error' in signed_semilla:
            return signed_semilla

        # 5. Aquí podrías añadir lógica para enviar el documento firmado a la DGII
        # ...

        return {
            'signed_document': sign_result['signed_xml'],
            'signed_semilla': signed_semilla['signed_xml']
        }