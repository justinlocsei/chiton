def resolve_binding(address, port=None):
    """Resolve an address and a port to a network binding.

    Args:
        address (str): The network address to use for the binding
        port (str): The port on which to bind

    Returns:
        str: The binding as an address:port string
    """
    bindings = [address, port]
    return ":".join([str(b) for b in bindings if b])
