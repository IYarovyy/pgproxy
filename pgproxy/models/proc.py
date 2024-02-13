import re
from dataclasses import dataclass, field
from typing import List

from pgproxy.console import err
from pgproxy.models.arg import Arg
from dataclasses import replace

MARKUP_PATTERN = r'---* RESULT FIELDS -* BEGIN --([\w\W]*)---* RESULT FIELDS -* END --'
SELECT_PATTERN = r'[Ss][Ee][Ll][Ee][Cc][Tt]([\w\W]*)[Ff][Rr][Oo][Mm]'


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
                    for rec_field in match.group(1).split(','):
                        name_type = rec_field.strip().split('::')
                        name = name_type[0][name_type[0].rfind('.') + 1:]

                        if len(name_type) > 1:
                            dtype = name_type[1]
                            self.__record_fields.append(Arg(name, dtype.lower(), 'OUT'))
                        else:
                            in_arg = self.__get_arg_from_list(name)
                            if in_arg:
                                self.__record_fields.append(replace(in_arg, mode='OUT'))
                            else:
                                err.print('Unknown type of field:{}, proc:{}.{}'.format(name,
                                                                                    self.schema,
                                                                                    self.name))

            return self.__record_fields
        else:
            return []

    def __get_arg_from_list(self, name: str):
        for arg in self.args:
            if arg.name == name:
                return arg
        return None
