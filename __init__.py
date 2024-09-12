from trytond.pool import Pool

__all__ = ['register']


def register():
    # Prevent import of backend when importing scripts
    from . import country

    Pool.register(
        country.Subdivision,
        module='country_uscensus', type_='model')
