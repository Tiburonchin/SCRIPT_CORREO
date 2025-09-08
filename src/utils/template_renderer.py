from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader, Template


class TemplateRenderer:
    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.env = Environment(loader=FileSystemLoader(str(template_path.parent)))
        self.template: Template = self.env.get_template(template_path.name)

    def render(self, context: Dict) -> str:
        return self.template.render(**context)

    def render_text(self, text: str, context: Dict) -> str:
        temp = self.env.from_string(text)
        return temp.render(**context)
