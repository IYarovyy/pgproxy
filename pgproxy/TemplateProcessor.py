import os
import placeholders
from mako.template import Template


class TemplateProcessor:
    def __init__(self, in_folder, out_folder, db_viewer):
        self.in_folder = in_folder
        self.out_folder = out_folder
        self.db_viewer = db_viewer

    def run(self):
        n = 0
        scope = {}
        for schema in self.db_viewer.schemas():
            procs = self.db_viewer.procs(schema)
            if len(procs) > 0:
                scope[schema] = {}
                for root, dirs, files in os.walk(self.in_folder):
                    for file in files:
                        if placeholders.is_schema_related_only(file):
                            n = n + 1
                            new_file_path = root.replace(self.in_folder, self.out_folder)
                            new_file_name = placeholders.interpret_name(file, n, schema)
                            os.makedirs(new_file_path, exist_ok=True)
                            with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                                file_template = Template(filename=os.path.join(root, file))
                                new_file.write(file_template.render(**{placeholders.SCHEMA: schema}))

            for proc in procs:
                args = self.db_viewer.args(schema, proc)
                scope[schema][proc] = args
                for root, dirs, files in os.walk(self.in_folder):
                    for file in files:
                        if placeholders.is_proc_related(file):
                            n = n + 1
                            new_file_path = root.replace(self.in_folder, self.out_folder)
                            new_file_name = placeholders.interpret_name(file, n, schema, proc)
                            os.makedirs(new_file_path, exist_ok=True)
                            with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                                file_template = Template(filename=os.path.join(root, file))
                                new_file.write(file_template.render(
                                    **{placeholders.SCHEMA: schema,
                                       placeholders.PROC: proc,
                                       placeholders.ARGS: args,
                                       }))
        for root, dirs, files in os.walk(self.in_folder):
            for file in files:
                if placeholders.is_after_all(file):
                    n = n + 1
                    new_file_path = root.replace(self.in_folder, self.out_folder)
                    new_file_name = placeholders.interpret_name(file, n)
                    os.makedirs(new_file_path, exist_ok=True)
                    with open(os.path.join(new_file_path, new_file_name), "w") as new_file:
                        file_template = Template(filename=os.path.join(root, file))
                        new_file.write(file_template.render(**{placeholders.SCOPE: scope}))
