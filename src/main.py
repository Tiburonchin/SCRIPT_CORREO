import argparse
import time
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

from utils.data_loader import load_contacts
from utils.mailer import Mailer
from utils.template_renderer import TemplateRenderer

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Envía correos personalizados desde Excel/CSV.")
    parser.add_argument("--excel", required=False, help="Ruta al archivo Excel (.xlsx) o CSV.")
    parser.add_argument(
        "--subject",
        required=False,
        default="🎓 Encuesta – Escuela de Posgrado UNAC | Admisión 2025-B | DNI {{ DNI }}",
        help="Asunto del correo. Soporta variables Jinja2 (p. ej., {{ Nombres }}).",
    )
    parser.add_argument("--template", default=str(Path(__file__).parent.parent / "templates" / "email.html.j2"), help="Ruta a plantilla HTML Jinja2.")
    parser.add_argument("--sheet", default=None, help="Nombre de la hoja (Excel). Por defecto, primera hoja.")
    parser.add_argument("--limit", type=int, default=None, help="Número máximo de correos a procesar.")
    parser.add_argument("--dry-run", action="store_true", help="Muestra vista previa sin enviar.")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Segundos de espera entre envíos.")
    parser.add_argument("--test-smtp", action="store_true", help="Probar conexión SMTP y autenticación.")
    return parser.parse_args()


def main():
    load_dotenv()  # Carga variables de entorno desde .env si existe

    args = parse_args()

    if args.test_smtp:
        try:
            mailer = Mailer()
            mailer.test_connection()
            console.print("[green]Conexión SMTP OK.[/green]")
        except Exception as e:
            console.print(f"[red]Fallo SMTP:[/red] {e}")
            sys.exit(1)
        sys.exit(0)

    if not args.excel:
        console.print("[red]Debes proporcionar --excel o usar --test-smtp.[/red]")
        sys.exit(1)

    excel_path = Path(args.excel)
    if not excel_path.exists():
        console.print(f"[red]No existe el archivo:[/red] {excel_path}")
        sys.exit(1)

    console.print("[bold]Cargando contactos...[/bold]")
    contacts = load_contacts(excel_path, sheet_name=args.sheet)
    if args.limit:
        contacts = contacts[: args.limit]

    if not contacts:
        console.print("[yellow]No se encontraron contactos válidos.[/yellow]")
        sys.exit(0)

    renderer = TemplateRenderer(Path(args.template))
    mailer: Optional[Mailer] = None
    if not args.dry_run:
        mailer = Mailer()

    # Vista previa de primeras filas
    preview_table = Table(title="Vista previa de contactos")
    for col in ["Nombres", "ApellidoPaterno", "ApellidoMaterno", "DNI", "Correo"]:
        preview_table.add_column(col)
    for row in contacts[: min(5, len(contacts))]:
        preview_table.add_row(
            str(row.get("Nombres", "")),
            str(row.get("ApellidoPaterno", "")),
            str(row.get("ApellidoMaterno", "")),
            str(row.get("DNI", "")),
            str(row.get("Correo", "")),
        )
    console.print(preview_table)

    total = 0
    ok = 0
    fail = 0

    for row in contacts:
        total += 1
        try:
            subject = renderer.render_text(args.subject, row)
            html = renderer.render(row)

            if args.dry_run:
                console.print(f"[cyan][DRY-RUN][/cyan] A: {row.get('Correo')} | Asunto: {subject}")
            else:
                assert mailer is not None
                mailer.send_email(to=row.get("Correo"), subject=subject, html=html)
                console.print(f"[green]Enviado[/green] ➜ {row.get('Correo')}")
                time.sleep(max(0.0, args.rate_limit))
            ok += 1
        except Exception as e:
            fail += 1
            console.print(f"[red]Error con {row.get('Correo')}: {e}")

    console.print(f"\n[bold]Resumen:[/bold] total={total}, ok={ok}, fail={fail}")


if __name__ == "__main__":
    main()
