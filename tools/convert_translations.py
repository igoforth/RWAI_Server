import json
import struct
import zlib
from pathlib import Path

import polib


def align_to_page(offset: int, page_size: int = 4096):
    return (offset + (page_size - 1)) // page_size * page_size


def adjust_metadata_offsets(
    metadata: dict[str, dict[str, int]],
    initial_metadata_size: int,
    page_size: int = 4096,
):
    """
    Adjusts metadata offsets to ensure that each is aligned to a page boundary,
    starting from an initial offset that accounts for previously written data.
    """
    current_offset = align_to_page(
        initial_metadata_size, page_size
    )  # Start from the aligned initial metadata size
    for locale in metadata:
        # Align the current offset to the nearest page boundary
        metadata[locale]["offset"] = current_offset
        # Increment the current offset by the length of this locale's data, then align again
        current_offset += metadata[locale]["length"]
        # Prepare the next offset
        current_offset = align_to_page(current_offset, page_size)

    return metadata


def compress_and_save_translations(base_path: Path, output_file: Path):
    metadata: dict[str, dict[str, int]] = {}
    compressed_data_segments: list[tuple[str, bytes]] = []

    offset = 4  # Initialize offset at 4 to give 4 bytes for metadata size int

    # Process translations and collect compressed data temporarily
    for locale_dir in base_path.iterdir():
        if locale_dir.is_dir():
            po_file_path = locale_dir / "LC_MESSAGES" / "messages.po"
            if po_file_path.exists():
                po = polib.pofile(str(po_file_path))
                locale_translations = {
                    entry.msgid.strip(): entry.msgstr for entry in po
                }
                json_data = json.dumps(locale_translations)
                compressed_data = zlib.compress(json_data.encode("utf-8"))
                compressed_data_segments.append((locale_dir.name, compressed_data))

                # Record length; offset to be finalized after metadata is fully defined
                metadata[locale_dir.name] = {
                    "offset": offset,
                    "length": len(compressed_data),
                }
                offset += len(compressed_data)  # Increment offset for the next block

    # Prepare metadata for final writing
    metadata_entries: list[bytes] = []
    for locale, info in metadata.items():
        # Pack locale, offset, and length into binary format
        packed_data = struct.pack(
            ">50sII",
            locale.encode("utf-8"),
            info["offset"],
            info["length"],
        )
        metadata_entries.append(packed_data)

    # Join all metadata entries and compress
    all_metadata = b"".join(metadata_entries)
    init_compressed_metadata = zlib.compress(all_metadata)
    init_metadata_size = len(init_compressed_metadata)
    init_metadata_padding = align_to_page(init_metadata_size)

    # Re-adjust each metadata offset to account for the metadata itself at the beginning
    metadata = adjust_metadata_offsets(metadata, init_metadata_size)

    # Prepare metadata for final writing
    metadata_entries: list[bytes] = []
    for locale, info in metadata.items():
        # Pack locale, offset, and length into binary format
        packed_data = struct.pack(
            ">50sII",
            locale.encode("utf-8"),
            info["offset"],
            info["length"],
        )
        metadata_entries.append(packed_data)

    # Join all metadata entries and compress
    all_metadata = b"".join(metadata_entries)
    compressed_metadata = zlib.compress(all_metadata)
    metadata_size = len(init_compressed_metadata)
    metadata_padding = align_to_page(metadata_size)

    # Check if sizes match
    if init_metadata_size != metadata_size:
        raise ValueError(
            f"Recompressed metadata size does not match the original ({init_metadata_size} vs {metadata_size}). Adjustment needed."
        )
    else:
        print(f"Metadata size: {metadata_size}")
    if init_metadata_padding != metadata_padding:
        raise ValueError(
            f"Recompressed metadata size does not match the original ({init_metadata_size} vs {metadata_size}). Adjustment needed."
        )
    else:
        print(f"Metadata padding: {metadata_padding}")

    # Write to file
    with output_file.open("wb") as file:
        # Write metadata size
        file.write(metadata_size.to_bytes(4, "big"))

        # Write metadata
        file.write(compressed_metadata)
        file.write(b"\x00" * metadata_padding)

        # Write compressed data blocks
        for data in compressed_data_segments:
            name: str = data[0]
            compressed_bytes: bytes = data[1]
            locale_metadata = metadata.get(name)
            if locale_metadata is None:
                raise RuntimeError("Locale metadata could not be determined")
            offset: int | None = locale_metadata.get("offset")
            if offset is None:
                raise RuntimeError("Locale offset in metadata could not be determined")
            length: int | None = locale_metadata.get("length")
            if length is None:
                raise RuntimeError("Locale length in metadata could not be determined")
            padding: int = align_to_page(length) - length
            print(
                f"Going to write padding {padding} for lang {name} with length {length}"
            )
            file.seek(offset)
            file.write(compressed_bytes)
            file.write(b"\x00" * padding)

    print("Translation writes finished")


def read_metadata_and_decompress_translation(output_file: Path, locale: str):
    with output_file.open("rb") as file:
        # Read metadata size
        metadata_size = struct.unpack(">I", file.read(4))[0]
        print(f"Found metadata size: {metadata_size}")

        # Read and decompress metadata
        compressed_metadata = file.read(metadata_size)
        decompressed_metadata = zlib.decompress(compressed_metadata)

        # Read specific locale metadata
        metadata: dict[str, dict[str, int]] = {}
        entry_size = (
            58  # Each entry is 50 bytes for locale + 4 for offset + 4 for length
        )
        for i in range(0, len(decompressed_metadata), entry_size):
            locale_bytes, offset, length = struct.unpack(
                ">50sII", decompressed_metadata[i : i + entry_size]
            )
            locale_str = locale_bytes.decode("utf-8").strip("\x00")
            metadata[locale_str] = {"offset": offset, "length": length}
        print(f"Found metadata: {metadata}")

        # Decompress specific locale
        locale_info: dict[str, int] = metadata[locale]
        file.seek(locale_info["offset"])
        compressed_data = file.read(locale_info["length"])
        decompressed_data = zlib.decompress(compressed_data)
        translations = json.loads(decompressed_data.decode("utf-8"))
        # print(f"Translations for locale '{locale}':", translations)

        return translations


# Usage example
if __name__ == "__main__":
    base_path = Path.cwd() / "locales"  # Path where `.po` files are stored
    output_file = (
        Path.cwd() / "build" / "AIServer" / "translations.json.zlib"
    )  # Output file for compressed translations

    # Compress and save translations
    compress_and_save_translations(base_path, output_file)

    # Read a specific locale's translations
    locale = "ru"  # Example locale
    print(f"Testing locale: {locale}")
    translations = read_metadata_and_decompress_translation(output_file, locale)
