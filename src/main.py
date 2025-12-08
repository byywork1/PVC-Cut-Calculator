from .loader import DimensionLoader
from .api import get_cut_length
from .config import EXCEL_PATH, SUPPORTED_TYPES

def prompt_nonempty(prompt_text: str):
    while True:
        v = input(prompt_text).strip()
        if v:
            return v
        print("Please enter a value.")

def main():
    loader = DimensionLoader(EXCEL_PATH)

    print("\n=== PVC CUT LENGTH CALCULATOR ===\n")
    print("Supported connection types:", ", ".join(SUPPORTED_TYPES))
    print("Enter sizes in inches (examples: 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8). Match the values used in your Database sheet.\n")

    type_a = prompt_nonempty("Connection Type A: ")
    size_a = prompt_nonempty("Connection Size A: ")

    type_b = prompt_nonempty("Connection Type B: ")
    size_b = prompt_nonempty("Connection Size B: ")

    # center-to-center validation
    while True:
        try:
            c2c = float(prompt_nonempty("Center-to-Center measurement (inches): "))
            break
        except ValueError:
            print("Please enter a numeric value for Center-to-Center.")

    request, cut_length = get_cut_length(loader, type_a, size_a, type_b, size_b, c2c)

    print("\n--- RESULT ---")
    print(request)
    print(f"\nFinal Cut Length = {cut_length} inches\n")

if __name__ == "__main__":
    main()
