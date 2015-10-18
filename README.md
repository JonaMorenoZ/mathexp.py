# mathexp.py

Python module to parse and evaluate mathematical expressions.

# Usage example

import mathexp

fx = mathexp.MathExp("x^2")

fx.add_variable("x", 3)

result = fx.evaluate()

print(result) <- prints 9.0

# Licensing

mathexp.py is released under the zlib license.
