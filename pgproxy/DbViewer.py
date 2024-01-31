import pgproxy.config as fields


class DbViewer:
    def __init__(self, config, connection):
        self.config = config
        self.connection = connection

    def schemas(self):
        with self.connection.cursor() as cursor:
            defined_pattern = self.config.get(fields.SCHEMAS_FIELD).get(fields.PATTERN_FIELD)
            defined_schemas = list(
                filter(lambda s: s not in fields.COMMON_SCHEMA_FIELDS,
                       self.config[fields.SCHEMAS_FIELD].keys()))
            if defined_pattern:
                # get schemas from DB by pattern
                cursor.execute("""select s.nspname as schema_name
                                        from pg_catalog.pg_namespace s
                                        join pg_catalog.pg_user u on u.usesysid = s.nspowner
                                        where nspname not in ('information_schema', 'pg_catalog', 'public')
                                              and nspname not like 'pg_toast%%'
                                              and nspname not like 'pg_temp_%%'
                                              and nspname like %s
                                        order by schema_name""", (defined_pattern,))
                defined_schemas = list(map(lambda s: s[0], cursor.fetchall()))
            elif not defined_schemas:
                # get all schemas from DB
                cursor.execute("""select s.nspname as schema_name
                                        from pg_catalog.pg_namespace s
                                        join pg_catalog.pg_user u on u.usesysid = s.nspowner
                                        where nspname not in ('information_schema', 'pg_catalog', 'public')
                                              and nspname not like 'pg_toast%%'
                                              and nspname not like 'pg_temp_%%'
                                        order by schema_name""")
                defined_schemas = list(map(lambda s: s[0], cursor.fetchall()))

            return defined_schemas

    def procs(self, schema):
        defined_procs = self.config.get(fields.SCHEMAS_FIELD).get(schema).get(fields.PROC_FIELD)

        proc_pattern = self.config.get(fields.SCHEMAS_FIELD).get(schema).get(fields.PATTERN_FIELD) \
                       or self.config.get(fields.SCHEMAS_FIELD).get(fields.PROC_PATTERN_FIELD)

        with self.connection.cursor() as cursor:
            if defined_procs:
                cursor.execute("""SELECT routine_schema As schema_name,
                            routine_name As procedure_name
                            FROM information_schema.routines
                            WHERE routine_type = 'PROCEDURE'
                            AND routine_name = ANY(%s)
                            AND routine_schema = %s;""", (defined_procs, schema))
            elif proc_pattern:
                cursor.execute("""SELECT routine_schema As schema_name,
                            routine_name As procedure_name
                            FROM information_schema.routines
                            WHERE routine_type = 'PROCEDURE'
                            AND routine_name LIKE %s
                            AND routine_schema = %s;""", (proc_pattern, schema))
            else:
                cursor.execute("""SELECT routine_schema As schema_name,
                                routine_name As procedure_name
                                FROM information_schema.routines
                                WHERE routine_type = 'PROCEDURE'
                                AND routine_schema = %s;""", (schema,))
            procs = list(map(lambda s: s[1], cursor.fetchall()))
        return procs

    def args(self, schema, proc):
        with self.connection.cursor() as cursor:
            cursor.execute("""select 
                                args.parameter_name::text,
                                args.data_type::text,
                                args.parameter_mode::text
                            from information_schema.routines proc
                            left join information_schema.parameters args
                                      on proc.specific_schema = args.specific_schema
                                      and proc.specific_name = args.specific_name
                            where proc.routine_schema = %s
                                and (proc.routine_type = 'PROCEDURE' or proc.routine_type = 'FUNCTION')
                                and (proc.routine_name = %s);""", (schema, proc))
            args = cursor.fetchall()
        return args
