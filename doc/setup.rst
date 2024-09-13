*****
Setup
*****

When the *Country US Census Module* is activated it does not create any
subdivision records. You do this using the provided script.

.. important::

   Before running this script, you must run the ``trytond_import_countries``
   script from the :doc:`Country Module <country:setup>` in order to populate
   the base `Country <country:model-country.country>` and `Subdivision
   <country:model-country.subdivision>` records.

.. _Loading and updating subdivisions:

Loading and updating subdivisions
=================================

The :command:`trytond_import_uscensus_subdivisions` script loads and updates
Tryton with the list of `Subdivisions <model-country.subdivision>` used by the
United States Census Bureau.

You run it with:

.. code-block:: sh

   trytond_import_uscensus_subdivisions -c trytond.conf -d <database> <two_letter_state_code>
