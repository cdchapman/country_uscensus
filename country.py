from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.tools import is_full_text, lstrip_wildcard


class Subdivision(metaclass=PoolMeta):
    __name__ = 'country.subdivision'
    _states = {
        'required': Eval('_parent_country.code') == 'US',
        'invisible': Eval('_parent_country.code') != 'US',
        }
    code_gnis = fields.Integer("Feature ID", states=_states,
            help="The GNIS Feature ID of the subdivision.")
    code_fips = fields.Char("FIPS Code", states=_states,
            help="The FIPS code of the subdivision.")
    fips_level = fields.Function(fields.Char("FIPS Level"),
            'on_change_with_fips_level', searcher='search_fips_level')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order.insert(0, ('code_fips', 'ASC'))
        cls.type.selection.extend([
            ('consolidated city-county', 'Consolidated city-county'),
            ('county subdivision', 'County subdivision'),
            ('incorporated place', 'Incorporated place'),
            ('independent city (united states)',
             'Independent city (United States)'),
        ])

    @classmethod
    def default_fips_level(cls):
        return 'unknown'

    @fields.depends('code_fips')
    def on_change_with_fips_level(self, name=None):
        levels = {
                2: 'state',
                3: 'county',
                5: 'place',
                }
        return levels.get(len(getattr(self, 'code_fips') or ''), 'unknown')

    @classmethod
    def search_fips_level(cls, name, clause):
        _, operator, value = clause
        match value:
            case 'county':
                code_len = 3
            case 'place':
                code_len = 5
            case _:
                code_len = 2

        return [('code_fips', 'like', '_' * code_len)]

    def get_rec_name(self, name):
        if self.code_fips:
            return '%s (%s)' % (self.name, self.code_fips)
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        _, operator, operand, *extra = clause
        if operator.startswith('!') or operator.startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        code_value = operand
        if operator.endswith('like') and is_full_text(operand):
            code_value = lstrip_wildcard(operand)
        return [bool_op,
            ('name', operator, operand, *extra),
            ('code', operator, code_value, *extra),
            ('code_fips', operator, code_value, *extra),
            ]
