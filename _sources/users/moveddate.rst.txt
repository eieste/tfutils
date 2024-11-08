==========
Moved Date
==========




Terraform
=========


.. code-block:: hcl
   :lineos:
   :caption:

   moved {
      to = ""
      from = ""
   }



.. code-block:: hcl
   :lineos:
   :caption:

   @moveddate(start="01-01-1970")
   moved {
      to = ""
      from = ""
   }



.. code-block:: hcl
   :lineos:
   :caption:

   @moveddate(start="01-01-1970", expire="19-01-2038")
   import {
      to = ""
      from = ""
   }


.. argparse::
   :module: tfutility.main
   :func: _get_parser_only
   :prog: tfutility
   :path: moveddate
