=======================
US Census Places Import
=======================

Imports::

    >>> from proteus import Model
    >>> from trytond.modules.country_uscensus.scripts import (
    ...     import_uscensus_subdivisions,)
    >>> from trytond.tests.tools import activate_modules

Activate modules::

    >>> config = activate_modules('country_uscensus')

Import places::

    >>> Country = Model.get('country.country')
    >>> us = Country(name="United States", code='US')
    >>> us.save()

    >>> Subdivision = Model.get('country.subdivision')
    >>> ut = Subdivision(name="Utah", code='US-UT', country=us)
    >>> ut.save()

    >>> import_uscensus_subdivisions.do_import(['ut'])
