import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re
_logger = logging.getLogger(__name__)

PATRON_CORREO = "\\w+([-+.]\\w+)*@\\w+([-.]\\w+)*\\.\\w+([-.]\\w+)"
PATRON_TELEFONO = "\\d{3}-\\d{3}-\\d{4}"
PATRON_RNC = "[0-9]{11}|[0-9]{9}"
PATRON_NUMEROPEDIDOINTERNO = "[0-9]{1,20}"
PATRON_MONTOIMPUESTO = "[0-9]{1,16}(\\.[0-9]{1,2})?"
PATRON_ITBIS = "[0-9]{1,2}"
PATRON_TASAIMPUESTO = "[0-9]{1,3}(.[0-9]{1,2})?"

class Account_FE_dom(models.TransientModel):
    _name = "account_fe.dom"
    _description = _("Account_FE.dom")

    # region ENCABEZADO
    Encabezado = fields.Char(_("Encabezado"))

    TipoeCF = fields.Selection(
        [
            ("31", _("Factura de Crédito Fiscal Electrónica")),
            ("32", _("Factura de Consumo Electrónica")),
            ("33", _("Nota de Débito Electrónica")),
            ("34", _("Nota de Crédito Electrónica")),
            ("41", _("Compras Electrónico")),
            ("43", _("Gastos Menores Electrónico")),
            ("44", _("Regímenes Especiales Electrónica")),
            ("45", _("Gubernamental Electrónico")),
            ("46", _("Comprobante para Exportaciones Electrónico")),
            ("47", _("Comprobante para Pagos al Exterior Electrónico")),
        ],
        string=_("Tipo de Comprobante"),
        required=True,
    )
    eNCF = fields.Char(_("eNCF"))

    FechaVencimientoSecuencia = fields.Date(_("Fecha de Vencimiento de la Secuencia"))

    IndicadorEnvioDiferido = fields.Boolean(_("Indicador de Envío Diferido"))

    IndicadorMontoGravado = fields.Boolean(_("Indicador de Monto Gravado"))


    TipoIngresos = fields.Selection(
        [
            ("01", _("Ingresos por operaciones (No financieros)")),
            ("02", _("Ingresos Financieros")),
            ("03", _("Ingresos Extraordinarios")),
            ("04", _("Ingresos por Arrendamientos")),
            ("05", _("Ingresos por Venta de Activo Depreciable")),
            ("06", _("Otros Ingresos")),
        ],
        string=_("Tipo de Ingresos"),
    )

    TipoPago = fields.Selection(S
        [
            ("1", _("Contado")),
            ("2", _("Crédito")),
            ("3", _("Gratuito")),
        ],
        string=_("Tipo de Pago"),
    )

    def Creacion_encabezado(self):
        
        Encabezado = self.Encabezado
        TipoeCF = self.TipoeCF
        eNCF = self.eNCF

        
    # region TABLA FORMASPAGO
    # ======================================== TablaFormasPago ========================================

    # a) Código Forma:
    #     1: Efectivo
    #     2: Cheque/Transferencia/Depósito
    #     3: Tarjeta de Débito/Crédito
    #     4: Venta a Crédito
    #     5: Bonos o Certificados de regalo
    #     6: Permuta
    #     7: Nota de crédito
    #     8: Otras Formas de pago
    #     Si la forma de pago corresponde al tipo
    #     5 el e-CF debe ser tipo 32.

    FormaPago = fields.Selection(
        [
            ("1", _("Efectivo")),
            ("2", _("Cheque/Transferencia/Depósito")),
            ("3", _("Tarjeta de Débito/Crédito")),
            ("4", _("Venta a Crédito")),
            ("5", _("Bonos o Certificados de regalo")),
            ("6", _("Permuta")),
            ("7", _("Nota de crédito")),
            ("8", _("Otras Formas de pago")),
        ],
        string=_("Forma de Pago"),
    )

    @api.onchange("FormaPago")
    def _onchange_formapago(self):
        if self.FormaPago == "5" and self.TipoeCF != "32":
            ValidationError(
                _(
                    "Si la forma de pago corresponde al Bonos o Certificados de regalo el e-CF debe ser Consumo Electrónica"
                )
            )

    MontoPago = fields.Float(_("Monto de Pago"))

    # ======================================== fin TablaFormasPago ========================================

    # Código Tipo:
    #     CT: Cta. Corriente
    #     AH: Ahorro
    #     OT: Otra

    TipoCuenta = fields.Selection(
        [
            ("CT", _("Cta. Corriente")),
            ("AH", _("Ahorro")),
            ("OT", _("Otra")),
        ],
        string=_("Tipo de Cuenta"),
    )

    NumeroCuentaPago = fields.Char(
        _("Número de Cuenta de Pago"),
        help="Número de la cuenta si la forma de pago es por cheque o transferencia bancaria.",
    )

    BancoPago = fields.Char(_("Banco de Pago"), help="Banco de la Cuenta")

    FechaDesde = fields.Date(_("Fecha Desde"))
    FechaHasta = fields.Date(_("Fecha Hasta"))

    TotalPaginas = fields.Integer(_("Total de Páginas"))
    
    # endregion

    # region EMISOR


    RNCEmisor = fields.Integer(_("RNC Emisor"), required=True)


    @api.onchange("RNCEmisor")
    def _onchange_rncemisor(self):
        print('===================================')
        # print(self.RNCEmisor)
        _logger.info('===================================')

        _logger.info(self.RNCEmisor)
        if self.RNCEmisor:
            if not re.match(PATRON_RNC, str(self.RNCEmisor)):
                raise ValidationError(_("El RNC debe tener 9 o 11 dígitos"))


    def test(self):
        
        RNCEmisor = self.RNCEmisor
        TipoeCF = self.TipoeCF

        print("RNCEmisor: ", RNCEmisor)
        print("TipoeCF: ", TipoeCF)


    RazonSocialEmisor = fields.Char(_("Razón Social Emisor"), required=True)

    # <xs:element name="RNCEmisor" type="RNCValidationType" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="RazonSocialEmisor" type="AlfNum150Type" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="NombreComercial" type="AlfNum150Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="Sucursal" type="AlfNum20Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="DireccionEmisor" type="AlfNum100Type" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="Municipio" type="ProvinciaMunicipioType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="Provincia" type="ProvinciaMunicipioType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TablaTelefonoEmisor" minOccurs="0" maxOccurs="1">
    # <xs:complexType>
    #      <xs:sequence>
    #        <xs:element name="TelefonoEmisor" type="TelefonoValidationType" minOccurs="1" maxOccurs="3"/>
    #      </xs:sequence>
    # </xs:complexType>
    # </xs:element>
    # <xs:element name="CorreoEmisor" type="CorreoValidationType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="WebSite" type="AlfNum50Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ActividadEconomica" type="AlfNum100Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="CodigoVendedor" type="AlfNum60Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="NumeroFacturaInterna" type="AlfNum20Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="NumeroPedidoInterno" type="Integer20ValidationType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ZonaVenta" type="AlfNum20Type" minOccurs="0"  maxOccurs="1"/>
    # <xs:element name="RutaVenta" type="AlfNum20Type" minOccurs="0"  maxOccurs="1"/>
    # <xs:element name="InformacionAdicionalEmisor" type="AlfNum250Type" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="FechaEmision" type="FechaValidationType" minOccurs="1" maxOccurs="1"/>

    NombreComercial = fields.Char(_("Nombre Comercial"))

    Sucursal = fields.Char(_("Sucursal"))

    DireccionEmisor = fields.Char(_("Dirección Emisor"), required=True)

    Municipio = fields.Char(_("Municipio"))

    Provincia = fields.Char(_("Provincia"))

    TelefonoEmisor = fields.Char(_("Teléfono Emisor"))


    @api.onchange("TelefonoEmisor")
    def _onchange_telefonoemisor(self):
        if not re.match(PATRON_TELEFONO, self.TelefonoEmisor):
            raise ValidationError(_("El teléfono debe tener el formato 000-000-0000"))

    CorreoEmisor = fields.Char(_("Correo Emisor"))
    

    @api.onchange("CorreoEmisor")
    def _onchange_correoemisor(self):
        if not re.match(PATRON_CORREO, self.CorreoEmisor):
            raise ValidationError(_("El correo debe tener el formato (xxx@xx.xx)"))

    WebSite = fields.Char(_("Web Site"))

    ActividadEconomica = fields.Char(_("Actividad Económica"))

    CodigoVendedor = fields.Char(_("Código Vendedor"))

    NumeroFacturaInterna = fields.Char(_("Número de Factura Interna"))

    NumeroPedidoInterno = fields.Integer(_("Número de Pedido Interno"))


    
    @api.onchange("NumeroPedidoInterno")
    def _onchange_numeropedidointerno(self):
        if not re.match(PATRON_NUMEROPEDIDOINTERNO, self.NumeroPedidoInterno):
            raise ValidationError(_("El número de pedido interno debe tener entre 1 y 20 dígitos"))

    ZonaVenta = fields.Char(_("Zona de Venta"))

    RutaVenta = fields.Char(_("Ruta de Venta"))

    InformacionAdicionalEmisor = fields.Char(_("Información Adicional Emisor"))

    FechaEmision = fields.Date(_("Fecha de Emisión"), required=True)

    


    # endregion
    
    # <xs:element name="Comprador" minOccurs="1" maxOccurs="1">
    #     <xs:complexType>
    #       <xs:sequence>
    #         <xs:element name="RNCComprador" type="RNCValidationType" minOccurs="1" maxOccurs="1"/>
    #         <xs:element name="RazonSocialComprador" type="AlfNum150Type" minOccurs="1" maxOccurs="1"/>
    #         <xs:element name="ContactoComprador" type="AlfNum80Type" minOccurs="0"  maxOccurs="1"/>
    #         <xs:element name="CorreoComprador" type="CorreoValidationType" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="DireccionComprador" type="AlfNum100Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="MunicipioComprador" type="ProvinciaMunicipioType" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="ProvinciaComprador" type="ProvinciaMunicipioType" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="FechaEntrega" type="FechaValidationType" minOccurs="0" maxOccurs="1"/>
    # 	            <xs:element name="ContactoEntrega" type="AlfNum100Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="DireccionEntrega" type="AlfNum100Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="TelefonoAdicional" type="TelefonoValidationType" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="FechaOrdenCompra" type="FechaValidationType" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="NumeroOrdenCompra" type="AlfNum20Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="CodigoInternoComprador" type="AlfNum20Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="ResponsablePago" type="Alfa20Type" minOccurs="0" maxOccurs="1"/>
    #         <xs:element name="InformacionAdicionalComprador" type="AlfNum150Type" minOccurs="0" maxOccurs="1"/>
    #       </xs:sequence>
    #     </xs:complexType>
    # </xs:element>


    # region COMPRADOR

    patron_RNCComprador = "[0-9]{11}|[0-9]{9}"


    RNCComprador = fields.Integer(_("RNC Comprador"))



    IdentificadorExtranjero = fields.Char(_("Identificador Extranjero"))

    @api.constrains("RNCComprador", "TipoeCF", "MontoPago", "IdentificadorExtranjero")
    def _constrains_rnccomprador(self):
        if not re.match(self.patron_RNCComprador, self.RNCComprador):
            raise ValidationError(_("El RNC debe tener 9 o 11 dígitos"))
        if self.TipoeCF == "32" and self.MontoPago >= 250000:
            if not self.RNCComprador:
                raise ValidationError(_("Debe indicar el RNC del comprador"))
        if self.TipoeCF in ["33", "34"]:
            if not self.RNCComprador and self.MontoPago >= 250000:
                raise ValidationError(_("Debe indicar el RNC del comprador"))
        if self.TipoeCF == "47" and self.IdentificadorExtranjero and self.RNCComprador:
            raise ValidationError(_("Si el comprador es extranjero, no puede tener RNC comprador"))




    # a) Si el e-CF es tipo 32 y el
    #     monto total es ≥
    #     DOP$250,000.00 se debe
    #     indicar el nombre o razón
    #     social comprador.
    # b) Si el e-CF tipo 33 y tipo 34
    #     modifica un e-CF tipo 32 con
    #     monto total ≥
    #     DOP$250,000.00, se debe
    #     indicar nombre o razón social
    #     comprador.


    # Nombre o Razón Social del comprador.
    # En caso de que el e-CF sea tipo 46, el
    # campo es condicional a que exista el
    # campo ‘RNC Comprador’ o
    # ‘Identificador Extranjero’.


    RazonSocialComprador = fields.Char(_("Razón Social Comprador"))

    @api.onchange("RazonSocialComprador")
    def _onchange_razonsocialcomprador(self):
        if self.TipoeCF == "32" and self.MontoPago >= 250000:
            if not self.RazonSocialComprador:
                raise ValidationError(_("Debe indicar la razón social del comprador"))
        if self.TipoeCF in ["33", "34"]:
            if not self.RazonSocialComprador:
                raise ValidationError(_("Debe indicar la razón social del comprador"))
        if self.TipoeCF == "46":
            if not self.RazonSocialComprador:
                raise ValidationError(_("Debe indicar la razón social del comprador"))



    # <xs:element name="MontoGravadoTotal" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoGravadoI1" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoGravadoI2" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoGravadoI3" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoExento" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ITBIS1" type="Integer2ValidationType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ITBIS2" type="Integer2ValidationType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ITBIS3" type="Integer2ValidationType" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBIS" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBIS1" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBIS2" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBIS3" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoImpuestoAdicional" type="Decimal18D1or2ValidationTypeMayorCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ImpuestosAdicionales" minOccurs="0" maxOccurs="1">

    # region TOTALES

    MontoGravadoTotal = fields.Float(_("Monto Gravado Total"))

    @api.onchange("MontoGravadoTotal")
    def _onchange_montogravadototal(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoGravadoTotal):
            raise ValidationError(_("El monto gravado total debe tener entre 1 y 16 dígitos"))

    MontoGravadoI1 = fields.Float(_("Monto Gravado I1"))

    @api.onchange("MontoGravadoI1")
    def _onchange_montogravadoi1(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoGravadoI1):
            raise ValidationError(_("El monto gravado I1 debe tener entre 1 y 16 dígitos"))

    MontoGravadoI2 = fields.Float(_("Monto Gravado I2"))

    @api.onchange("MontoGravadoI2")
    def _onchange_montogravadoi2(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoGravadoI2):
            raise ValidationError(_("El monto gravado I2 debe tener entre 1 y 16 dígitos"))
    
    MontoGravadoI3 = fields.Float(_("Monto Gravado I3"))

    @api.onchange("MontoGravadoI3")
    def _onchange_montogravadoi3(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoGravadoI3):
            raise ValidationError(_("El monto gravado I3 debe tener entre 1 y 16 dígitos"))
    
    MontoExento = fields.Float(_("Monto Exento"))

    @api.onchange("MontoExento")
    def _onchange_montoexento(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoExento):
            raise ValidationError(_("El monto exento debe tener entre 1 y 16 dígitos"))


    ITBIS1 = fields.Integer(_("ITBIS1"))

    @api.onchange("ITBIS1")
    def _onchange_itbis1(self):
        if not re.match(PATRON_ITBIS, self.ITBIS1):
            raise ValidationError(_("El ITBIS1 debe tener entre 1 y 2 dígitos"))

    ITBIS2 = fields.Integer(_("ITBIS2"))

    @api.onchange("ITBIS2")
    def _onchange_itbis2(self):
        if not re.match(PATRON_ITBIS, self.ITBIS2):
            raise ValidationError(_("El ITBIS2 debe tener entre 1 y 2 dígitos"))

    ITBIS3 = fields.Integer(_("ITBIS3"))

    @api.onchange("ITBIS3")
    def _onchange_itbis3(self):
        if not re.match(PATRON_ITBIS, self.ITBIS3):
            raise ValidationError(_("El ITBIS3 debe tener entre 1 y 2 dígitos"))

    TotalITBIS = fields.Float(_("Total ITBIS"))

    @api.onchange("TotalITBIS")
    def _onchange_totalitbis(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBIS):
            raise ValidationError(_("El total ITBIS debe tener entre 1 y 16 dígitos"))

    TotalITBIS1 = fields.Float(_("Total ITBIS1"))

    @api.onchange("TotalITBIS1")
    def _onchange_totalitbis1(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBIS1):
            raise ValidationError(_("El total ITBIS1 debe tener entre 1 y 16 dígitos"))

    TotalITBIS2 = fields.Float(_("Total ITBIS2"))

    @api.onchange("TotalITBIS2")
    def _onchange_totalitbis2(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBIS2):
            raise ValidationError(_("El total ITBIS2 debe tener entre 1 y 16 dígitos"))

    TotalITBIS3 = fields.Float(_("Total ITBIS3"))

    @api.onchange("TotalITBIS3")
    def _onchange_totalitbis3(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBIS3):
            raise ValidationError(_("El total ITBIS3 debe tener entre 1 y 16 dígitos"))
    
    MontoImpuestoAdicional = fields.Float(_("Monto Impuesto Adicional"))

    @api.onchange("MontoImpuestoAdicional")
    def _onchange_montoimpuestoadicional(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoImpuestoAdicional):
            raise ValidationError(_("El monto impuesto adicional debe tener entre 1 y 16 dígitos"))



    # region TABLA IMPUESTOSADICIONALES
    # ======================================== ImpuestosAdicionales ========================================

    # <xs:element name="TipoImpuesto" type="CodificacionTipoImpuestosType" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="TasaImpuestoAdicional" type="Decimal5D1or2ValidationTypeMayorCero" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="MontoImpuestoSelectivoConsumoEspecifico" type="Decimal18D1or2ValidationTypeMayorCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoImpuestoSelectivoConsumoAdvalorem" type="Decimal18D1or2ValidationTypeMayorCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="OtrosImpuestosAdicionales" type="Decimal18D1or2ValidationTypeMayorCero" minOccurs="0" maxOccurs="1"/>

    TipoImpuesto = fields.Selection(
        [
            ("001", _("Propina Legal")),
            ("002", _("Contribución al Desarrollo de las Telecomunicaciones Ley 153-98 Art. 45")),
            ("003", _("Servicios Seguros en general")),
            ("004", _("Servicios de Telecomunicaciones")),
            ("005", _("Expedición de la primera placa")),
            ("006", _("Cerveza")),
            ("007", _("Vinos de uva")),
            ("008", _("Vermut y demás vinos de uvas frescas")),
            ("009", _("Demás bebidas fermentadas")),
            ("010", _("Alcohol Etílico sin desnaturalizar (Mayor o igual a 80%)")),
            ("011", _("Alcohol Etílico sin desnaturalizar (inferior a 80%)")),
            ("012", _("Aguardientes de uva")),
            ("013", _("Whisky")),
            ("014", _("Ron y demás aguardientes de caña")),
            ("015", _("Gin y Ginebra")),
            ("016", _("Vodka")),
            ("017", _("Licores")),
            ("018", _("Los demás (Bebidas y Alcoholes)")),
            ("019", _("Cigarrillos que contengan tabaco cajetilla 20 unidades")),
            ("020", _("Los demás Cigarrillos que contengan 20 unidades")),
            ("021", _("Cigarrillos que contengan 10 unidades")),
            ("022", _("Los demás Cigarrillos que contengan 10 unidades")),
            ("023", _("Cerveza")),
            ("024", _("Vinos de uva")),
            ("025", _("Vermut y demás vinos de uvas frescas")),
            ("026", _("Demás bebidas fermentadas")),
            ("027", _("Alcohol Etílico sin desnaturalizar (Mayor o igual a 80%)")),
            ("028", _("Alcohol Etílico sin desnaturalizar (inferior a 80%)")),
            ("029", _("Aguardientes de uva")),
            ("030", _("Whisky")),
            ("031", _("Ron y demás aguardientes de caña")),
            ("032", _("Gin y Ginebra")),
            ("033", _("Vodka")),
            ("034", _("Licores")),
            ("035", _("Los demás (Bebidas y Alcoholes)")),
            ("036", _("Cigarrillos que contengan tabaco cajetilla 20 unidades")),
            ("037", _("los demas Cigarrillos que contengan 20 unidades")),
            ("038", _("Cigarrillos que contengan 10 unidades")),
            ("039", _("Los demás Cigarrillos que contengan 10 unidades")),

        ]
    )

    TasaImpuestoAdicional = fields.Float(_("Tasa Impuesto Adicional"))

    @api.onchange("TasaImpuestoAdicional")
    def _onchange_tasaimpuestoadicional(self):
        if not re.match(PATRON_TASAIMPUESTO, self.TasaImpuestoAdicional):
            raise ValidationError(_("La tasa de impuesto adicional debe tener entre 1 y 3 dígitos"))
        
    MontoImpuestoSelectivoConsumoEspecifico = fields.Float(_("Monto Impuesto Selectivo Consumo Específico"))

    @api.onchange("MontoImpuestoSelectivoConsumoEspecifico")
    def _onchange_montoimpuestoselectivoconsumoespecifico(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoImpuestoSelectivoConsumoEspecifico):
            raise ValidationError(_("El monto impuesto selectivo consumo específico debe tener entre 1 y 16 dígitos"))

    MontoImpuestoSelectivoConsumoAdvalorem = fields.Float(_("Monto Impuesto Selectivo Consumo Advalorem"))

    @api.onchange("MontoImpuestoSelectivoConsumoAdvalorem")
    def _onchange_montoimpuestoselectivoconsumoadvalorem(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoImpuestoSelectivoConsumoAdvalorem):
            raise ValidationError(_("El monto impuesto selectivo consumo advalorem debe tener entre 1 y 16 dígitos"))

    OtrosImpuestosAdicionales = fields.Float(_("Otros Impuestos Adicionales"))

    @api.onchange("OtrosImpuestosAdicionales")
    def _onchange_otrosimpuestosadicionales(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.OtrosImpuestosAdicionales):
            raise ValidationError(_("Los otros impuestos adicionales deben tener entre 1 y 16 dígitos"))
            

    # ======================================== FIN ImpuestosAdicionales ========================================

    # <xs:element name="MontoTotal" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="1" maxOccurs="1"/>
    # <xs:element name="MontoNoFacturable" type="Decimal18D1or2ValidationTypeNegativoPositivo" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoPeriodo" type="Decimal18D1or2ValidationTypeNegativoPositivo" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="SaldoAnterior" type="Decimal18D1or2ValidationTypeNegativoPositivo" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="MontoAvancePago" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="ValorPagar" type="Decimal18D1or2ValidationTypeNegativoPositivo" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBISRetenido" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalISRRetencion" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalITBISPercepcion" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
    # <xs:element name="TotalISRPercepcion" type="Decimal18D1or2ValidationTypeMayorIgualCero" minOccurs="0" maxOccurs="1"/>
                  
    MontoTotal = fields.Float(_("Monto Total"), required=True)

    @api.onchange("MontoTotal")
    def _onchange_montototal(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoTotal):
            raise ValidationError(_("El monto total debe tener entre 1 y 16 dígitos"))

    MontoNoFacturable = fields.Float(_("Monto No Facturable"))

    @api.onchange("MontoNoFacturable")
    def _onchange_montonofacturable(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.MontoNoFacturable):
            raise ValidationError(_("El monto no facturable debe tener entre 1 y 16 dígitos"))

    TotalITBISRetenido = fields.Float(_("Total ITBIS Retenido"))

    @api.onchange("TotalITBISRetenido")
    def _onchange_totalitbisretenido(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBISRetenido):
            raise ValidationError(_("El total ITBIS retenido debe tener entre 1 y 16 dígitos"))

    TotalITBISPercepcion = fields.Float(_("Total ITBIS Percepción"))

    @api.onchange("TotalITBISPercepcion")
    def _onchange_totalitbispercepcion(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalITBISPercepcion):
            raise ValidationError(_("El total ITBIS percepción debe tener entre 1 y 16 dígitos"))

    TotalISRRetencion = fields.Float(_("Total ISR Retención"))

    @api.onchange("TotalISRRetencion")
    def _onchange_totalisrretencion(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalISRRetencion):
            raise ValidationError(_("El total ISR retención debe tener entre 1 y 16 dígitos"))

    TotalISRPercepcion = fields.Float(_("Total ISR Percepción"))

    @api.onchange("TotalISRPercepcion")
    def _onchange_totalisrpercepcion(self):
        if not re.match(PATRON_MONTOIMPUESTO, self.TotalISRPercepcion):
            raise ValidationError(_("El total ISR percepción debe tener entre 1 y 16 dígitos"))

    


    