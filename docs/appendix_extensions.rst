.. _appendix_extensions:

.. |br| raw:: html

    <br />

***************************
:mod:`Sphinx` -- Extensions
***************************

We have described in the previous section the extensions:
:ref:`intersphinx <intersphinx_extension>`,
:ref:`extlinks <extlinks_extension>`,
:ref:`ifconfig <ifconfig_extension>`.

.. index::
   pair: extension; graphviz

Graphs with :index:`Graphviz`
=============================

The `Graphviz
<http://graphviz.org/>`_
`graph drawing Sphinx extension
<http://sphinx.pocoo.org/ext/graphviz.html>`_ is provided in Sphinx distribution.

To enable the extension we have to add it to the ``extensions`` list in
``conf.py``::

  extensions = ['sphinx.est.graphviz']

It uses directly the dot command to process `DOT language
<http://graphviz.org/content/dot-language>`_.


Examples
--------

.. sidebar::  graph

   Undirected::

      .. graph:: foo

         "bar" -- "baz";

   Directed::

      .. digraph:: foo

         "bar" -> "baz";

.. graph:: foo

   "bar" -- "baz";

.. digraph:: foo

   "bar" -> "baz";

