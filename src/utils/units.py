def convert_cpu_units_to_nanocores(cpus: str | int) -> int:
    """
    Convert CPU units in cores, millicores, microcores, or nanocores to nanocores.
    
    Args:
    cpus (str | int): CPU value in cores, millicores, microcores, or nanocores (e.g., "1", "100m", "100u", "1000000000n") or as an integer.
    
    Returns:
    int: CPU value in nanocores.
    """
    # If the input is an integer, it's assumed to be in cores
    if isinstance(cpus, int):
        return cpus * 1_000_000_000  # 1 core = 1_000_000_000 nanocores
    
    # If the input is a string
    elif isinstance(cpus, str):
        if cpus.endswith('m'):  # Millicores
            return int(cpus[:-1]) * 1_000_000  # Remove 'm' and convert
        elif cpus.endswith('u'):  # Microcores
            return int(cpus[:-1]) * 1_000  # Remove 'u' and convert
        elif cpus.endswith('n'):  # Nanocores
            return int(cpus[:-1])  # Just remove 'n'
        else:  # Cores
            return int(cpus) * 1_000_000_000
    else:
        raise ValueError("Unsupported type. The input must be a string or an integer.")


def convert_decimal_unit_to_bytes(unit: str | int) -> int:
    """
    Convert a decimal unit to bytes. Supports k, M, G, T, P, E suffixes for decimal units.
    
    Args:
    - unit (str | int): The unit to convert. Can be an integer or string with suffix.
    
    Returns:
    - int: Equivalent number of bytes.
    
    Raises:
    - ValueError: If the unit is invalid or suffix is unknown.
    """
    conversion_factors = {
        'k': 10**3,
        'M': 10**6,
        'G': 10**9,
        'T': 10**12,
        'P': 10**15,
        'E': 10**18
    }
    if isinstance(unit, int):
        return unit
    if isinstance(unit, str) and unit[:-1].isdigit() and unit[-1] in conversion_factors:
        number_part = int(unit[:-1])
        suffix = unit[-1]
        return number_part * conversion_factors[suffix]
    else:
        raise ValueError(f"Invalid unit or unknown suffix: {unit}")


def convert_binary_unit_to_bytes(unit: str | int) -> int:
    """
    Convert binary unit to bytes. Supports Ki, Mi, Gi, Ti, Pi, Ei suffixes for binary units.
    
    Args:
    - unit (str | int): The unit to convert. Can be an integer or string with suffix.
    
    Returns:
    - int: Equivalent number of bytes.
    
    Raises:
    - ValueError: If the unit is invalid or suffix is unknown.
    """
    conversion_factors = {
        'Ki': 2**10,
        'Mi': 2**20,
        'Gi': 2**30,
        'Ti': 2**40,
        'Pi': 2**50,
        'Ei': 2**60
    }
    if isinstance(unit, int):
        return unit
    if isinstance(unit, str):
        for suffix in conversion_factors:
            if unit.endswith(suffix):
                number_part = int(unit[:-len(suffix)])
                return number_part * conversion_factors[suffix]
        raise ValueError(f"Invalid unit or unknown suffix: {unit}")
    else:
        raise ValueError("Unit must be an integer or a string with a valid binary suffix.")


def convert_storage_unit_to_bytes(unit: str | int | float) -> int | float:
    """
    Convert a storage unit to bytes, automatically determining if the unit is binary or decimal.
    
    Args:
    - unit (str | int | float): The unit to convert. Can be an integer, float, or string with suffix.
    
    Returns:
    - int | float: The equivalent number of bytes.
    
    Raises:
    - ValueError: If the unit is a string with an invalid or unknown suffix.
    """
    binary_suffixes = ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']
    decimal_suffixes = ['k', 'M', 'G', 'T', 'P', 'E']
    
    if isinstance(unit, int) or isinstance(unit, float):
        return unit
    
    for suffix in binary_suffixes:
        if unit.endswith(suffix):
            return convert_binary_unit_to_bytes(unit)
    
    for suffix in decimal_suffixes:
        if unit.endswith(suffix):
            return convert_decimal_unit_to_bytes(unit)
    
    raise ValueError(f"Invalid unit or unknown suffix: {unit}")

