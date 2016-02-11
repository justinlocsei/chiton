from django.test import TestCase

from chiton.utils import network


class ResolveBindingTestCase(TestCase):

    def test_address_and_port(self):
        """It produces a colon-separated binding from an address and port."""
        binding = network.resolve_binding("1.2.3.4", port=80)
        self.assertEqual(binding, "1.2.3.4:80")

    def test_port_string(self):
        """It handles a quoted port value."""
        binding = network.resolve_binding("1.2.3.4", port="80")
        self.assertEqual(binding, "1.2.3.4:80")

    def test_address_only(self):
        """It produces a binding without a port when given only an address."""
        binding = network.resolve_binding("1.2.3.4")
        self.assertEqual(binding, "1.2.3.4")

    def test_null_args(self):
        """It returns an empty string when given empty arguments."""
        binding = network.resolve_binding("", port="")
        self.assertEqual(binding, "")
