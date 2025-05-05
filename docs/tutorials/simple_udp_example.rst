[device_communication] Tutorial: UDP
====================================

1. Make sure you have installed the required dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

2. Navigate to the `examples/` directory and run the script
   (please also provide any "UDP echo server" listening on port 12345 and responding on port 54321):

    .. code-block:: bash

      python simple_udp_usage.py

    .. literalinclude:: ../../examples/simple_udp_usage.py
       :language: python
       :linenos: