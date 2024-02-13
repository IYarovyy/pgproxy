import os
from dataclasses import replace

from .console import out
from .placeholders import *
from mako.template import Template


class TemplateProcessor:
    def __init__(self, in_folder, out_folder, db_viewer):
        self.in_folder = in_folder
        self.out_folder = out_folder
        self.db_viewer = db_viewer

    def run(self):
        n = 0
        scope_procs = []
        with out.status("[bold green]Working..."):
            for schema in self.db_viewer.schemas():
                out.rule("Schema: {}".format(schema))
                procs = self.db_viewer.procs(schema)
                if len(procs) > 0:
                    for root, dirs, files in os.walk(self.in_folder):
                        for file in files:
                            if is_schema_related_only(file):
                                n = n + 1
                                new_file_path = root.replace(self.in_folder, self.out_folder, 1)
                                new_file_name = interpret_name(file, n, schema)
                                os.makedirs(new_file_path, exist_ok=True)
                                with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                                    file_template = Template(filename=os.path.join(root, file))
                                    new_file.write(file_template.render(**{SCHEMA: schema}))

                for proc in procs:
                    args = self.db_viewer.args(proc)
                    rich_proc = replace(proc, args=args)
                    scope_procs.append(rich_proc)

                    for root, dirs, files in os.walk(self.in_folder):
                        for file in files:
                            if is_proc_related(file):
                                n = n + 1
                                new_file_path = root.replace(self.in_folder, self.out_folder, 1)
                                new_file_name = interpret_name(file, n, schema, rich_proc.name)
                                os.makedirs(new_file_path, exist_ok=True)
                                with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                                    file_template = Template(filename=os.path.join(root, file))
                                    new_file.write(file_template.render(
                                        **{PROC: rich_proc}))
                    out.print("[green]:heavy_check_mark: {}[/green]".format(proc.name))
            for root, dirs, files in os.walk(self.in_folder):
                for file in files:
                    if is_after_all(file):
                        n = n + 1
                        new_file_path = root.replace(self.in_folder, self.out_folder, 1)
                        new_file_name = interpret_name(file, n)
                        os.makedirs(new_file_path, exist_ok=True)
                        with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                            file_template = Template(filename=os.path.join(root, file))
                            new_file.write(file_template.render(**{PROCS: scope_procs}))
