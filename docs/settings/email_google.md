# 📧 Configuración de Gmail (SMTP)

Para usar Gmail como proveedor SMTP en PulseCore, necesitas crear una **Contraseña de Aplicación**. Sigue estos pasos detallados:

## Paso 1: Activar Verificación en Dos Pasos

Ve a la configuración de seguridad de tu cuenta de Google: [myaccount.google.com/security](https://myaccount.google.com/security)

![Configuración de Seguridad](https://storage.googleapis.com/smtp_mailer/smtp_gmail_1.png)

Activa la **Verificación en dos pasos** si no la tienes habilitada. Es un requisito obligatorio para crear contraseñas de aplicación.

## Paso 2: Buscar Contraseñas de Aplicación

En la misma página de seguridad, busca "Contraseñas de aplicaciones" en el buscador o ve directamente a: [myaccount.google.com/apppasswords](https://myaccount.google.com/u/1/apppasswords)

![Buscar Contraseñas de Aplicación](https://storage.googleapis.com/smtp_mailer/smtp_gmail_2.png)

## Paso 3: Crear Nueva Contraseña

1. Selecciona "Otra (nombre personalizado)"
2. Dale un nombre descriptivo como "PulseCore API"
3. Haz clic en "Generar"
4. **Copia la contraseña de 16 caracteres** - esta será tu `SMTP_PASSWORD`.

![Crear Contraseña de Aplicación](https://storage.googleapis.com/smtp_mailer/smtp_gmail_3.png)

## Paso 4: Configuración Final en el Archivo `.env`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # La contraseña de 16 caracteres generada
SMTP_USE_TLS=true
```

> [!CAUTION]
> **Seguridad**: Guarda la contraseña de aplicación inmediatamente. Una vez que cierres la ventana, no podrás volver a verla. Nunca subas esta contraseña a repositorios públicos.

**Referencias oficiales:**
- [Configurar cliente de correo con Gmail](https://support.google.com/mail/answer/7126229)
- [Enviar correo desde aplicaciones](https://support.google.com/a/answer/176600?hl=es)
