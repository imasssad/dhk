# -*- coding: utf-8 -*-
###############################################################################
# Author : Laxicon Solution. (<https://www.laxicon.in/>)
# Copyright(c): 2015-Today Laxicon Solution.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.laxicon.in/license>
###############################################################################

# from . import models
# from . import wizard
from . import report


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '16.0':
        raise Warning(
            'Module support Odoo series 16.0 found {}.'.format(server_serie))
    return True
