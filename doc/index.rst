###############
USCensus Module
###############

The *Country US Census Module* augments Tryton_'s *Country* module with
geographical feature data used by the `United States Census Bureau`_.

Included in these data are two code series organized around three geographic
levels: *state*, *county*, and *place*. The first series, known historically as
FIPS codes, are maintained by the InterNational Committee for Information
Technology Standards (INCITS_). The second, known as Georgraphic Names
Information System (GNIS) codes, is maintained by the United States Geological
Survey (USGS_).

This module imports FIPS codes as they were defined for the 2020 census.

=========  ===================  =========================
  Level      Withdrawn FIPS       Replacement Standard
=========  ===================  =========================
 State      FIPS 5–2 (1987)      INCITS 28–2009 (R2019)
 County     FIPS 6–4 (1990)      INCITS 31–2009 (R2019)
 Place      FIPS 55-DC3 (1994)   INCITS 446–2008 (R2018)
=========  ===================  =========================

.. _United States Census Bureau: https://www.census.gov/library/reference/code-lists/ansi.html

.. https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html

.. _INCITS: https://www.incits.org/

.. _USGS: https://www.usgs.gov/us-board-on-geographic-names/domestic-names

.. toctree::
   :maxdepth: 2

   setup
   design
   releases
