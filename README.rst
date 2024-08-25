falcon-sync
===========

``falcon-sync`` is a utility library for bridging sync (WSGI) and async (ASGI)
Falcon components.

This library is provided primarily for compatibility purposes, where parts of
an application have not been migrated to, e.g., ``async`` yet; also in the
cases where a specific paradigm is enforced by a third party library (e.g., the
dependency in question only supports ``async``, or conversely, does not support
it at all).

.. warning::
    This project is in the early stages of development.

    There is not *that* much to see here (yet).
