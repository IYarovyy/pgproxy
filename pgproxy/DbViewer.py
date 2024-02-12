import pgproxy.config as fields
from pgproxy.models.arg import Arg
from pgproxy.models.proc import Proc


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
        defined_procs = self.config.get(fields.SCHEMAS_FIELD, {}).get(schema, {}).get(fields.PROC_FIELD)

        proc_pattern = self.config.get(fields.SCHEMAS_FIELD, {}).get(schema, {}).get(fields.PATTERN_FIELD) \
                       or self.config.get(fields.SCHEMAS_FIELD, {}).get(fields.PROC_PATTERN_FIELD)

        select_query = "SELECT routine_schema As schema_name, " \
                       "routine_name As procedure_name, " \
                       "routine_type As procedure_type, " \
                       "routine_definition As procedure_definition, " \
                       "data_type As data_type " \
                       "FROM information_schema.routines """

        with self.connection.cursor() as cursor:
            if defined_procs:
                cursor.execute("{} WHERE (routine_type = 'PROCEDURE' OR routine_type = 'FUNCTION')"
                               " AND routine_name = ANY(%s) "
                               "AND routine_schema = %s;".format(select_query), (defined_procs, schema))
            elif proc_pattern:
                cursor.execute("{} WHERE (routine_type = 'PROCEDURE' OR routine_type = 'FUNCTION')"
                               "AND routine_name LIKE %s "
                               "AND routine_schema = %s;".format(select_query), (proc_pattern, schema))
            else:
                cursor.execute("{} WHERE (routine_type = 'PROCEDURE' OR routine_type = 'FUNCTION') "
                               "AND routine_schema = %s;".format(select_query), (schema,))
            procs = list(map(lambda s: Proc(s[0], s[1], s[2], s[3], s[4]), cursor.fetchall()))
        return procs

    def args(self, proc):
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
                                and (proc.routine_name = %s);""", (proc.schema, proc.name))
            args = list(map(lambda s: Arg(s[0], s[1], s[2]), cursor.fetchall()))
        return args
