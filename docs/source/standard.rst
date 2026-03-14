Driver standards
========

Each adapter should follow these rules :

- A driver is a class, its name must start with the brand name capitalized if there's one
- Each I/O operation must be a method. Cached values can be implemented with properties. Setters are prohibited for IO operations
- Properties are reserved for constant properties (serial numbers, constants, etc...)