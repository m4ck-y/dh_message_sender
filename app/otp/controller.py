from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
from datetime import datetime
from app.config import settings
from app.otp.models import OTPEmailRequest, OTPEmailResponse
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = "app/templates"

class EmailOTPApplication:
    def __init__(self):
        print(f"[INFO] Inicializando EmailOTPApplication con templates en: {TEMPLATES_DIR}")
        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    def send_otp_email(self, request: OTPEmailRequest) -> OTPEmailResponse:
        """
        Envía email OTP con configuración avanzada y personalización completa.
        
        Procesa la solicitud OTP aplicando lógica condicional para mostrar/ocultar
        elementos según los parámetros proporcionados (expiración, verificación automática, logo).
        
        Args:
            request (OTPEmailRequest): Configuración completa del email OTP.
            
        Returns:
            OTPEmailResponse: Resultado detallado del envío con metadatos.
        """
        try:
            template = self.jinja_env.get_template("otp.html")
            
            # Logo y app_name siempre desde configuración
            
            # Determinar si mostrar mensaje de expiración
            show_expiry = request.expiry_minutes is not None and request.expiry_minutes > 0
            
            # Determinar si mostrar botón de redirección automática
            show_redirect_button = request.redirect_url is not None and request.redirect_url.strip() != ""
            
            # Construir contexto para la plantilla
            context = {
                "email": request.email,
                "otp_code": request.code,
                "app_name": settings.APP_NAME,  # Desde .env
                "logo_url": settings.COMPANY_LOGO_URL,  # Desde .env
                "expiry_minutes": request.expiry_minutes,
                "show_expiry": show_expiry,
                "redirect_url": request.redirect_url,
                "show_redirect_button": show_redirect_button,
                "company_name": settings.COMPANY_NAME,
                "support_email": settings.SUPPORT_EMAIL,
                "website_url": settings.WEBSITE_URL
            }
            
            print(f"[INFO] Contexto del template: {context}")
            html_content = template.render(context)
            
            # Crear el mensaje
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = request.email
            #msg['Subject'] = f'Código de verificación - {settings.APP_NAME}'
            msg['Subject'] = "Codigo de verificación"
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar el correo
            print(f"[INFO] SMTP_USE_SSL: {settings.SMTP_USE_SSL}")
            print(f"[INFO] SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
            print(f"[INFO] SMTP_PORT: {settings.SMTP_PORT}")
            
            if settings.SMTP_USE_SSL:
                # Método para puerto 465: Conexión segura desde el inicio
                print("[INFO] Conectando con SMTP_SSL")
                ssl_context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    settings.SMTP_HOST, 
                    settings.SMTP_PORT, 
                    context=ssl_context,
                    timeout=settings.SMTP_TIMEOUT
                )
            elif settings.SMTP_USE_TLS:
                # Método para puerto 587: Conexión normal que se actualiza a segura
                print("[INFO] Conectando con SMTP + TLS")
                server = smtplib.SMTP(
                    settings.SMTP_HOST, 
                    settings.SMTP_PORT, 
                    timeout=settings.SMTP_TIMEOUT
                )
                print("[INFO] Iniciando STARTTLS")
                server.starttls()
            else:
                # Conexión no segura (no recomendada)
                print("[WARN] Conectando sin seguridad - SMTP plano")
                server = smtplib.SMTP(
                    settings.SMTP_HOST, 
                    settings.SMTP_PORT, 
                    timeout=settings.SMTP_TIMEOUT
                )

            # Autenticar y enviar el correo
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            result = server.sendmail(settings.SMTP_FROM_EMAIL, request.email, msg.as_string())
            server.quit()
            
            # Verificar resultado del envío
            if not result:
                print(f"[INFO] Correo enviado exitosamente a {request.email}")
                
                # Construir respuesta exitosa
                return OTPEmailResponse(
                    success=True,
                    message="Código OTP enviado exitosamente",
                    email_sent_to=request.email,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    expiry_minutes=request.expiry_minutes,
                    has_verification_button=show_redirect_button,
                    logo_used=settings.COMPANY_LOGO_URL
                )
            else:
                print(f"[ERROR] Fallo en el envío a: {result}")
                raise Exception(f"Error SMTP: {result}")
                
        except Exception as e:
            print(f"[ERROR] Error enviando OTP: {str(e)}")
            
            # Construir respuesta de error
            return OTPEmailResponse(
                success=False,
                message=f"Error enviando código OTP: {str(e)}",
                email_sent_to=request.email,
                timestamp=datetime.utcnow().isoformat() + "Z",
                expiry_minutes=request.expiry_minutes,
                has_verification_button=show_redirect_button if 'show_redirect_button' in locals() else False,
                logo_used=settings.COMPANY_LOGO_URL
            )

    # Método legacy para compatibilidad hacia atrás
    def Send_OTP(self, email: str, code: str, app_name: str):
        """
        Método legacy para compatibilidad hacia atrás.
        
        DEPRECATED: Usar send_otp_email() con OTPEmailRequest en su lugar.
        """
        print("[WARN] Usando método legacy Send_OTP - considerar migrar a send_otp_email()")
        
        # Crear request con parámetros básicos (app_name ya no se necesita)
        request = OTPEmailRequest(
            email=email,
            code=code
        )
        
        # Llamar al método nuevo
        response = self.send_otp_email(request)
        
        # Si hay error, lanzar excepción para mantener compatibilidad
        if not response.success:
            raise Exception(response.message)