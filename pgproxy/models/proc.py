import re
from dataclasses import dataclass, field
from dataclasses import replace
from typing import List

from pgproxy.console import err
from pgproxy.models.arg import Arg

MARKUP_PATTERN = r'---* RESULT FIELDS -* BEGIN --([\w\W]*)---* RESULT FIELDS -* END --'
SELECT_PATTERN = r'[Ss][Ee][Ll][Ee][Cc][Tt]([\w\W]*)[Ff][Rr][Oo][Mm]'
FIELD_PATTERN = r'(\w*)\s*::\s*(\w*)\s*(?:[aA][sS]\s*(\w*))?'


@dataclass(frozen=True)
class Proc:
    schema: str
    name: str
    type: str
    definition: str
    data_type: str
    args: List[Arg] = field(default_factory=list)
    __record_fields: List[Arg] = field(default_factory=list)

    def get_record_fields(self):
        if (type(self.data_type) == str) and (self.data_type.lower() == 'record'):
            if len(self.__record_fields) == 0:
                match = re.search(MARKUP_PATTERN, self.definition)
                if match is None:
                    match = re.search(SELECT_PATTERN, self.definition)
                if match:
                    for rec_field in match.group(1).split('\n'):
                        rec_field = rec_field.strip()
                        if not rec_field.startswith("--") and rec_field:
                            field_match = re.search(FIELD_PATTERN, rec_field)
                            if field_match:
                                query_field_name = field_match.group(1)
                                field_type = field_match.group(2)
                                assigned_field_name = field_match.group(3)

                                if assigned_field_name:
                                    name = assigned_field_name
                                else:
                                    name = query_field_name

                                if name:
                                    if field_type:
                                        self.__record_fields.append(Arg(name, field_type.lower(), 'OUT'))
                                    else:
                                        in_arg = self.__get_arg_from_list(name)
                                        if in_arg:
                                            self.__record_fields.append(replace(in_arg, mode='OUT'))
                                        else:
                                            err.print('Unknown type of field:{}, proc:{}.{}'
                                                      .format(name, self.schema, self.name))
                                else:
                                    err.print('Unknown name of field record:', rec_field)
                            else:
                                err.print('Unknown format of field record:', rec_field)
            return self.__record_fields
        else:
            return []

    def __get_arg_from_list(self, name: str):
        for arg in self.args:
            if arg.name == name:
                return arg
        return None
