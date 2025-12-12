from .loader import DimensionLoader
from .api import get_cut_length, get_lay_in_cuts, get_bushing_cut
from .config import EXCEL_PATH, SUPPORTED_CONNECTOR_TYPES
from fractions import Fraction

def prompt_nonempty(prompt_text: str):
    while True:
        v = input(prompt_text).strip()
        if v:
            return v
        print("Please enter a value.")

def select_connector_type(prompt_text: str = "Select connector type") -> str:
    """
    Display a dropdown-style menu of supported connector types and return the selection.
    """
    print(f"\n{prompt_text}:")
    for i, conn_type in enumerate(SUPPORTED_CONNECTOR_TYPES, 1):
        print(f"  {i}) {conn_type}")
    
    choice = None
    while choice not in range(1, len(SUPPORTED_CONNECTOR_TYPES) + 1):
        try:
            choice = int(prompt_nonempty(f"Choose option (1-{len(SUPPORTED_CONNECTOR_TYPES)}): "))
        except ValueError:
            print(f"Please enter a number between 1 and {len(SUPPORTED_CONNECTOR_TYPES)}.")
    
    return SUPPORTED_CONNECTOR_TYPES[choice - 1]

def reduce_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    """
    Reduce a fraction to its simplest form using GCD.
    Example: reduce_fraction(8, 16) returns (1, 2)
    """
    from math import gcd
    common_divisor = gcd(numerator, denominator)
    return (numerator // common_divisor, denominator // common_divisor)

def decimal_to_fraction_16ths(decimal: float) -> str:
    """
    Convert a decimal to a fraction with denominator 16, reduced to simplest form.
    Uses Fraction for precise arithmetic to avoid floating-point rounding errors.
    Example: 2.3125 returns "2 5/16"; 2.5 returns "2 1/2" (not "2 8/16")
    """
    # Convert to Fraction for precise arithmetic
    frac = Fraction(decimal).limit_denominator(1000)
    
    # Convert to 16ths
    frac_16ths = frac * 16
    whole = int(frac_16ths) // 16
    remainder = int(frac_16ths) % 16
    
    if remainder == 0:
        return str(whole)
    else:
        # Reduce the fraction to simplest form
        num, denom = reduce_fraction(remainder, 16)
        return f"{whole} {num}/{denom}"

def main():
    loader = DimensionLoader(EXCEL_PATH)

    print("\n=== PVC CUT LENGTH CALCULATOR ===\n")
    
    # Choose calculation type
    print("Select cut type:")
    print("  1) Standard (single cut)")
    print("  2) Lay-in (two cuts)")
    print("  3) Bushing (subtract bushing thickness)")
    calc_choice = None
    while calc_choice not in {"1", "2", "3"}:
        calc_choice = prompt_nonempty("Choose option (1/2/3): ")

    type_a = select_connector_type("Connection Type A")
    size_a = prompt_nonempty("Connection Size A (inches): ")

    type_b = select_connector_type("Connection Type B")
    size_b = prompt_nonempty("Connection Size B (inches): ")

    # handle each calculation type
    if calc_choice == "1":
        # center-to-center validation for standard
        while True:
            try:
                c2c = float(prompt_nonempty("Center-to-Center measurement (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for Center-to-Center.")

        request, cut_length = get_cut_length(loader, type_a, size_a, type_b, size_b, c2c)

        # Ask about shave
        shave_choice = prompt_nonempty("Include shave in calculation? (y/n): ").lower()
        if shave_choice == "y":
            cut_length -= 1/16

        print("\n--- RESULT ---")
        print(request)
        print(f"\nFinal Cut Length = {decimal_to_fraction_16ths(cut_length)} inches\n")

    elif calc_choice == "2":
        # lay-in needs overall C2C and lay-in C2C plus lay-in offset
        while True:
            try:
                c2c_overall = float(prompt_nonempty("Overall Center-to-Center measurement (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for Overall Center-to-Center.")
        while True:
            try:
                c2c_lay_in = float(prompt_nonempty("Lay-in Center-to-Center (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for Lay-in Center-to-Center.")
        while True:
            try:
                lay_in_offset = float(prompt_nonempty("Lay-in offset (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for Lay-in offset.")

        request, (cut1, cut2) = get_lay_in_cuts(loader, type_a, size_a, type_b, size_b,
                                                c2c_overall, c2c_lay_in, lay_in_offset)

        # Ask about shave
        shave_choice = prompt_nonempty("Include shave in calculation? (y/n): ").lower()
        if shave_choice == "y":
            cut1 -= 1/16
            cut2 -= 1/16

        print("\n--- RESULT (Lay-in) ---")
        print(request)
        print(f"\nCut 1 = {decimal_to_fraction_16ths(cut1)} inches")
        print(f"Cut 2 = {decimal_to_fraction_16ths(cut2)} inches\n")

    else:
        # bushing calculation
        while True:
            try:
                c2c = float(prompt_nonempty("Center-to-Center measurement (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for Center-to-Center.")
        while True:
            try:
                bushing = float(prompt_nonempty("Bushing thickness (inches): "))
                break
            except ValueError:
                print("Please enter a numeric value for bushing thickness.")

        request, cut_length = get_bushing_cut(loader, type_a, size_a, type_b, size_b, c2c, bushing)

        # Ask about shave
        shave_choice = prompt_nonempty("Include shave in calculation? (y/n): ").lower()
        if shave_choice == "y":
            cut_length -= 1/16

        print("\n--- RESULT (Bushing) ---")
        print(request)
        print(f"\nFinal Cut Length = {decimal_to_fraction_16ths(cut_length)} inches\n")

if __name__ == "__main__":
    main()
