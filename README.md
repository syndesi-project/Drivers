# Syndesi drivers Python package

This package contains the official Syndesi Drivers



## Folder structure


- ``test_and_measurement``
  - ``multimeters``
  - ``oscilloscopes``
  - ``powersupplies``
  - ``sourcemeters``
  - ``waveform_generators``
- ``motion``
  - ``controllers``
- ``environmental``
  - ``ovens``
- ``imaging``
- ``industrial``
  - ``io_modules``






## Driver structure

```python
class DeviceName(Interfaces):
    def __init__(self, adapter : Adapter) -> None:
        """
        Device description
        """
        super().__init__()

        # Check the adapter type here
        assert isinstance(adapter, ...), "Invalid adapter"

        # Use a protocol
        self._prot = SCPI(adapter)
        #self._prot = Raw(adapter)

    # Declare a method
    def my_method(self) -> int:
        """
        Method description
        """
        self._prot.write('...')
        data = self._prot.read('...')
        return int(data)
```