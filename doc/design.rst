******
Design
******

The *Country US Census Module* extends the following concept:

.. _model-country.subdivision:

Subdivision
===========

The *Subdivision* concept is extended to store the :abbr:`Federal Information
Processing Standard (FIPS)` code and :abbr:`Geographical Name Information System
(GNIS)` Feature ID.

.. seealso::

   The `Subdivision <country:model-country.subdivision>` concept is introduced
   by the :doc:`Country Module <country:index>`.

.. tip::

   FIPS codes for smaller geographical entities are usually unique within
   larger geographic entities. For that reason, county and place FIPS codes are
   only unique within their respective state.

   Also, FIPS codes are hierarchical whereas GNIS Feature IDs are assigned
   sequentially, based on the date of entry into the database.

   More info on these geo-identifiers:

   - https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html
   - https://www.census.gov/library/reference/code-lists/class-codes.html
