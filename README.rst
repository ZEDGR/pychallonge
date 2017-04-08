pychal
===========

.. image:: https://img.shields.io/travis/ZEDGR/pychal.svg
   :target: https://travis-ci.org/ZEDGR/pychal

Pychal is a drop-in replacement of pychallonge
with some extra features and support for new Python versions.
Pychal provides python bindings for the
`CHALLONGE! <http://challonge.com>`__
`API <http://api.challonge.com/v1>`__.



Differences
===========
The only diffence with the pychallonge is the
dictionary keys with dashes are now with undescores
for example the key 'created-at' is now 'created_at'.

Requirements
============

-  ``iso8601``
-  ``tzlocal``
-  ``pytz``
-  ``requests``

Python version support
======================

-  ``2.7``
-  ``3.4+``

Installation
============

For the stable version

::

    pip install pychal

For latest development

::

    pip install -e git+http://github.com/ZEDGR/pychal#egg=pychal

Usage
=====

.. code:: python

    import challonge

    # Tell pychal about your [CHALLONGE! API credentials](http://api.challonge.com/v1).
    challonge.set_credentials("your_challonge_username", "your_api_key")

    # Retrieve a tournament by its id (or its url).
    tournament = challonge.tournaments.show(3272)

    # Tournaments, matches, and participants are all represented as normal Python dicts.
    print(tournament["id"]) # 3272
    print(tournament["name"]) # My Awesome Tournament
    print(tournament["started_at"]) # None

    # Retrieve the participants for a given tournament.
    participants = challonge.participants.index(tournament["id"])
    print(len(participants)) # 13

    # Start the tournament and retrieve the updated information to see the effects
    # of the change.
    challonge.tournaments.start(tournament["id"])
    tournament = challonge.tournaments.show(tournament["id"])
    print(tournament["started_at"]) # 2011-07-31 16:16:02-04:00

See `challonge.com <http://api.challonge.com/v1>`__ for full API
documentation.

API Issues
==========

The Challonge API has some issues with the attachments endpoints. The
``create`` and ``update`` endpoints are not working correctly. When you
try to upload an attachment with asset(file) the API returns 500
internal server error. The same happens with asset + description.
This problem has been reported to Challonge.

Other problems that I have noticed is that the check in process through
the API seems weird. When you undo check in a participant the field
'checked_in' remains True but in the website the participant is
correctly not checked in. That's why I haven't write any tests about
check in. Another problem is that in matches ``show`` endpoint 
the 'include_attachments' parameter is not behaving correctly.

Fixed by pychal: In the datetime fields the api returns
random timezone offsets, pychal convert those
to your machine's local time. Also you can set any timezone
you want with ``set_timezone`` function.

Running the unit tests
======================

Pychal comes with a set of unit tests. The tests are not
comprehensive, but do utilize each method and verify basic
functionality.

In order to test behavior of the python bindings, API calls must be made
to CHALLONGE!, which requires a username and api key. To run the tests
with your credentials, set ``CHALLONGE_USER`` and ``CHALLONGE_KEY``
appropriately in your environment.

::

    $ git clone http://github.com/ZEDGR/pychal pychal
    $ CHALLONGE_USER=my_user CHALLONGE_KEY=my_api_key python pychal/tests.py
    ...............................
    ----------------------------------------------------------------------
    Ran 31 tests in 98.176s

    OK

Note that several tournaments are created, published, started, and
completed over the course of the unit tests. These should be cleaned up
by the end, but if any of the tests fail they may not be cleaned up. As
long as the basic functions work, you can clean up errant tournaments as
follows.

.. code:: python

       import challonge
       challonge.set_credentials("my_user", "my_api_key")
       for t in challonge.tournaments.index():
           if t["name"].startswith("pychal"):
               challonge.tournaments.destroy(t["id"])
