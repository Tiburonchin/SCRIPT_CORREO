# Envío de correos personalizados desde Excel/CSV (Python)

Este proyecto envía correos electrónicos personalizados a una lista de destinatarios definida en un archivo Excel (.xlsx) o CSV, usando Gmail (SMTP) con contraseña de aplicación (2 pasos). El contenido del correo se personaliza con Nombres, Apellido Paterno, Apellido Materno y DNI.

## Requisitos
- Windows con PowerShell
- Python 3.9+ instalado
- Una contraseña de aplicación de Gmail (2FA activado). No compartas tu contraseña.

## Campos requeridos en el Excel/CSV
El archivo debe tener columnas equivalentes a:
- Apellido paterno
- Apellido materno
- Nombres
- DNI
- Correo

Notas:
- Se toleran variaciones de mayúsculas/minúsculas, espacios y acentos. Ej.: "Apellido Paterno", "apellido paterno", "APELLIDO PATERNO".
- También se acepta CSV con separador coma.

## Configuración
1) Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example` y rellena tus datos:

- SMTP_HOST: smtp.gmail.com
- SMTP_PORT: 587
- SMTP_USER: tu_correo@gmail.com
- SMTP_PASSWORD: tu contraseña de aplicación de 16 caracteres (no tu contraseña normal)
- FROM_NAME: Nombre que verán los destinatarios (opcional)
- REPLY_TO: Dirección de respuesta (opcional)

## Instalación
En PowerShell, desde la carpeta del proyecto:

```powershell
# (Opcional) Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Uso
Prepara tu archivo de datos, por ejemplo `data\contactos.xlsx` o `data\contactos.csv`.

 Opciones principales:
- `--excel`: ruta al archivo Excel o CSV.
- `--subject`: asunto del correo (opcional; por defecto: "🎓 Encuesta – Escuela de Posgrado UNAC | Admisión 2025-B | DNI {{ DNI }}"). Soporta variables Jinja2: {{ Nombres }}, {{ DNI }}, etc.
- `--template`: ruta a la plantilla HTML Jinja2.
- `--dry-run`: no envía; muestra vista previa.
- `--rate-limit`: segundos a esperar entre envíos (por defecto 1.0).
- `--limit`: tope de correos a procesar.

Ejemplos:

```powershell
# Ensayo (dry-run) con CSV de ejemplo
python src/main.py --excel data/sample_contactos.csv --subject "Hola {{ Nombres }}" --dry-run

# Envío real usando la plantilla incluida
python src/main.py --excel data/sample_contactos.csv --template templates/email.html.j2 --rate-limit 1.5

# Alternativas de asunto decorado
python src/main.py --excel data/sample_contactos.csv --subject "🎓 Encuesta de Opinión – Escuela de Posgrado UNAC | Admisión 2025-B | DNI {{ DNI }}" --template templates/email.html.j2 --rate-limit 1.5
python src/main.py --excel data/sample_contactos.csv --subject "[UNAC – Posgrado] Encuesta 2025-B ➜ {{ Nombres }} (DNI {{ DNI }})" --template templates/email.html.j2 --rate-limit 1.5
```

## Personalización de la plantilla

Edita `templates/email.html.j2`. Variables disponibles por fila:

- `Nombres`, `ApellidoPaterno`, `ApellidoMaterno`, `DNI`, `Correo` (y cualquier columna adicional)

Puedes usar lógica Jinja2 básica si lo necesitas.

## Buenas prácticas de seguridad

- Nunca publiques tu `.env` ni la contraseña de aplicación.
- Usa `--dry-run` para validar antes de enviar.

## Solución de problemas

- Error de autenticación: verifica que usas contraseña de aplicación (no la normal) y que `SMTP_USER` coincide con tu Gmail.
- Bloqueo/limitación: aumenta `--rate-limit` para evitar límites.
- Columnas no detectadas: revisa nombres y que el archivo no tenga hojas/columnas vacías.

## Licencia

MIT
