
from pathlib import Path

from ai_service.app.input.input_processor import process_input


def print_header():
    print("\n" + "=" * 65)
    print("                    TRUTHCAMS AI")
    print("                 INPUT PROCESSING DEMO")
    print("=" * 65)


def print_result(result):
    print("\n" + "-" * 65)
    print("PROCESSING RESULT")
    print("-" * 65)

    print(f"Input type : {result.get('input_type', 'Unknown')}")

    metadata = result.get("metadata", {})
    print(f"Status     : {metadata.get('status', 'Unknown')}")

    print("\nEXTRACTED TEXT")
    print("-" * 65)

    extracted_text = result.get("extracted_text", "")

    if extracted_text and extracted_text.strip():
        print(extracted_text)
    else:
        print("No text was extracted.")

    print("\nERROR")
    print("-" * 65)
    print(metadata.get("error") or "None")

    print("=" * 65)


def process_text():
    print("\n[TEXT INPUT]")
    print("Enter your text below.")
    print("Type END on a separate line to finish.")
    print("Type CANCEL to return to the main menu.\n")

    lines = []

    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return

        if line.strip().upper() == "CANCEL":
            print("Returning to main menu.")
            return

        if line.strip().upper() == "END":
            break

        lines.append(line)

    user_text = "\n".join(lines).strip()

    if not user_text:
        print("Error: Text input cannot be empty.")
        return

    try:
        result = process_input(
            user_input=user_text,
            input_type="text"
        )
        print_result(result)

    except Exception as exc:
        print(f"\nText processing failed: {type(exc).__name__}: {exc}")


def process_image():
    print("\n[IMAGE INPUT]")
    print("Enter the full path to your image.")
    print("Type CANCEL to return to the main menu.\n")

    image_path = input("Image path: ").strip()

    image_path = image_path.strip('"').strip("'")

    if image_path.upper() == "CANCEL":
        print("Returning to main menu.")
        return

    if not image_path:
        print("Error: Image path cannot be empty.")
        return

    path = Path(image_path).expanduser()

    if not path.exists():
        print(f"Error: File does not exist: {path}")
        return

    if not path.is_file():
        print("Error: The selected path is not a file.")
        return

    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    if path.suffix.lower() not in allowed_extensions:
        print("Error: Unsupported image format.")
        return

    try:
        result = process_input(
            user_input=str(path.resolve()),
            input_type="image"
        )
        print_result(result)

    except Exception as exc:
        print(f"\nImage processing failed: {type(exc).__name__}: {exc}")


def main():
    while True:
        print_header()

        print("1. Enter text")
        print("2. Select image")
        print("0. Exit")

        print("-" * 65)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            process_text()

        elif choice == "2":
            process_image()

        elif choice == "0":
            print("\nThank you for using Truthcams AI.")
            print("Exiting...")
            break

        else:
            print("\nInvalid option. Please enter 1, 2, or 0.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
