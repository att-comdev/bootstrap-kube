Configuration
=============

Promenade is configured using a set of Deckhand_ compatible configuration
documents and a bootstrapping Armada_ manifest that is responsible for
deploying core components into the cluster.

Details about Promenade-specific documents can be found here:

.. toctree::
    :maxdepth: 2
    :caption: Documents

    docker
    genesis
    images
    kubernetes-network
    kubernetes-node
    system-packages


The provided Armada_ manifest and will be applied on the genesis node as soon
as it is healthy.


.. _Armada: https://github.com/att-comdev/armada
.. _Deckhand: https://github.com/att-comdev/deckhand
