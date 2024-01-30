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
