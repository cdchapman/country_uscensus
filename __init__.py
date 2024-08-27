from trytond.pool import Pool

__all__ = ['register']


def register():
    # Prevent import of backend when importing scripts
    from . import census

    Pool.register(
        census.ClassCode,
        census.Place,
        census.Region,
        module='country_uscensus', type_='model')
    Pool.register(
        module='country_uscensus', type_='wizard')
    Pool.register(
        module='country_uscensus', type_='report')
